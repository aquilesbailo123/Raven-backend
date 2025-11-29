import logging
from django.conf import settings
from django.http import Http404
from rest_framework import status
from dj_rest_auth.registration.views import VerifyEmailView
from django.views.generic import TemplateView
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _, activate as translation_activate, get_language as translation_get_language
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from allauth.account.models import EmailAddress
from django.db.models import Model
from django.contrib.auth import get_user_model

from users.cache_keys import RESEND_VERIFICATION_TOKEN_CACHE_KEY
from users.models import Startup, Profile, Evidence, FinancialInput, InvestorPipeline
from users.serializers.startup import StartupOnboardingSerializer, StartupSerializer
from users.serializers.onboarding import (
    OnboardingWizardSerializer,
    EvidenceSerializer,
    FinancialInputSerializer,
    InvestorPipelineSerializer
)

logger = logging.getLogger(__name__)

User: Model = get_user_model()

class CustomVerifyEmailView(VerifyEmailView):
    """
    Expands the original dj_rest_auth VerifyEmailView to:
    1. Verify the email using the provided key.
    2. Generate and return authentication tokens for automatic login.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.kwargs['key'] = serializer.validated_data['key']
        
        try:
            confirmation = self.get_object()
        except Http404:
            return Response({'detail': _('Invalid confirmation key.')}, status=status.HTTP_404_NOT_FOUND)

        confirmation.confirm(self.request)
        
        user = confirmation.email_address.user

        if not user.is_active:
            return Response({'detail': _('User account is inactive.')}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token_str = str(refresh.access_token)
        refresh_token_str = str(refresh)

        response_data = {
            'detail': _('Email verified successfully. You are now logged in.'),
            'access_token': access_token_str,
            'refresh_token': refresh_token_str,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ResendEmailConfirmationView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request: Request):
        token = request.data.get('token')
        if not token:
            return Response({'Status': False, 'code': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = cache.get(f'{RESEND_VERIFICATION_TOKEN_CACHE_KEY}{token}')
        if not user_id:
            return Response({'Status': False, 'code': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)

        # check if verification email in progress
        verification_in_progress = cache.get(f'{RESEND_VERIFICATION_TOKEN_CACHE_KEY}{user_id}')
        if verification_in_progress:
            return Response({'Status': False, 'code': 'Email confirmation in progress'}, status=status.HTTP_400_BAD_REQUEST)

        lang = request.data.get('lang', 'en')
        if lang not in dict(settings.LANGUAGES):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'result': f'Lang {lang} not found'})

        # Activate the language for this request
        translation_activate(lang)
        setattr(request, 'LANGUAGE_CODE', translation_get_language())

        user = User.objects.get(id=user_id)
        email_address: EmailAddress = EmailAddress.objects.get(
            user=user,
            email=user.email,
        )
        if email_address.verified:
            return Response({'Status': False, 'code': 'Email already verified'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Sending email confirmation to {user.email}")
        email_address.send_confirmation(request)

        # set verification in progress by user id
        cache.set(f'{RESEND_VERIFICATION_TOKEN_CACHE_KEY}{user_id}', 1, timeout=300)  # 5 min for next attempt
        return Response({'Status': True}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(TemplateView):
    template_name = 'accounts/password_reset_confirm.html'

    def get(self, request, *args, **kwargs):
        # Make the token and uid available to the template
        context = self.get_context_data(**kwargs)
        context['token'] = kwargs.get('token')
        context['uid'] = kwargs.get('uidb64')
        return self.render_to_response(context)


class StartupOnboardingView(APIView):
    """
    API endpoint for startup onboarding.
    Allows authenticated startup users to complete their onboarding by providing company_name and industry.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """Get current startup information and onboarding status"""
        try:
            profile = request.user.profile

            # Check if user is a startup
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create startup
            startup, created = Startup.objects.get_or_create(profile=profile)

            serializer = StartupSerializer(startup)
            return Response({
                'startup': serializer.data,
                'is_onboarding_complete': startup.is_onboarding_complete()
            }, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {'detail': _('Profile not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request: Request):
        """Complete startup onboarding by providing company_name and industry"""
        try:
            profile = request.user.profile

            # Check if user is a startup
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create startup
            startup, created = Startup.objects.get_or_create(profile=profile)

            # Validate and update data
            serializer = StartupOnboardingSerializer(startup, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Return full startup data
            full_serializer = StartupSerializer(startup)
            return Response({
                'detail': _('Onboarding completed successfully.'),
                'startup': full_serializer.data,
                'is_onboarding_complete': startup.is_onboarding_complete()
            }, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {'detail': _('Profile not found.')},
                status=status.HTTP_404_NOT_FOUND
            )


class OnboardingCompleteView(APIView):
    """
    API endpoint for completing the full onboarding wizard (Phase 2).

    This endpoint replaces all mock data with real data from the startup.
    It handles a single POST request containing:
    - TRL/CRL evidence
    - Financial projections
    - Investor pipeline

    After successful completion, the startup's is_mock_data flag is set to False.

    **Authentication Required**: Yes
    **User Type**: Startup only

    **POST Body Structure**:
    ```json
    {
        "current_trl": 3,
        "target_funding_amount": 150000.00,
        "evidences": [
            {
                "trl_level": 3,
                "description": "Proof of concept completed",
                "file_url": "https://storage.example.com/evidence.pdf"
            }
        ],
        "financial_data": [
            {
                "period_date": "2024-01-31",
                "revenue": 5000.00,
                "costs": 8000.00,
                "cash_balance": 45000.00,
                "monthly_burn": 3000.00
            }
        ],
        "investors": [
            {
                "investor_name": "Angel Investor 1",
                "investor_email": "investor@example.com",
                "stage": "CONTACTED",
                "ticket_size": 50000.00
            }
        ]
    }
    ```
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        """
        Complete the onboarding wizard by:
        1. Validating all nested data
        2. Deleting existing mock data
        3. Creating real data from the wizard
        4. Updating startup.is_mock_data to False
        """
        try:
            profile = request.user.profile

            # Security check: Only startup users can access this endpoint
            if profile.user_type != Profile.STARTUP:
                logger.warning(
                    f"Non-startup user {request.user.email} attempted to access onboarding wizard"
                )
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create startup instance
            startup, created = Startup.objects.get_or_create(profile=profile)

            # Log the onboarding attempt
            logger.info(
                f"Onboarding wizard started for startup: {startup.company_name or 'Unnamed'} "
                f"(ID: {startup.id}, User: {request.user.email})"
            )

            # Validate and process the complete wizard data
            serializer = OnboardingWizardSerializer(
                data=request.data,
                context={'startup': startup, 'request': request}
            )

            # Validate all nested data
            serializer.is_valid(raise_exception=True)

            # Create all data (this also deletes mock data and updates startup)
            result = serializer.save()

            # Log successful completion
            logger.info(
                f"Onboarding wizard completed successfully for startup: "
                f"{startup.company_name} (ID: {startup.id}). "
                f"Created: {len(result['evidences'])} evidences, "
                f"{len(result['financial_data'])} financial periods, "
                f"{len(result['investors'])} investors"
            )

            # Return success response with serialized data
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Profile.DoesNotExist:
            logger.error(f"Profile not found for user: {request.user.email}")
            return Response(
                {'detail': _('Profile not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Unexpected error in onboarding wizard for user {request.user.email}: {str(e)}",
                exc_info=True
            )
            return Response(
                {'detail': _('An error occurred while processing your onboarding data.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StartupDataView(APIView):
    """
    Get startup data for authenticated startup users.
    Returns company info, TRL, and basic stats.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            startup = Startup.objects.filter(profile=profile).first()
            if not startup:
                return Response(
                    {'detail': _('Startup not found.')},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StartupSerializer(startup)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching startup data for {request.user.email}: {str(e)}", exc_info=True)
            return Response(
                {'detail': _('An error occurred while fetching startup data.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EvidenceListView(APIView):
    """
    Get all evidences for the authenticated startup user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            startup = Startup.objects.filter(profile=profile).first()
            if not startup:
                return Response([], status=status.HTTP_200_OK)

            evidences = Evidence.objects.filter(startup=startup).order_by('-created')
            serializer = EvidenceSerializer(evidences, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching evidences for {request.user.email}: {str(e)}", exc_info=True)
            return Response(
                {'detail': _('An error occurred while fetching evidences.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FinancialDataListView(APIView):
    """
    Get all financial data for the authenticated startup user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            startup = Startup.objects.filter(profile=profile).first()
            if not startup:
                return Response([], status=status.HTTP_200_OK)

            financial_data = FinancialInput.objects.filter(startup=startup).order_by('-period_date')
            serializer = FinancialInputSerializer(financial_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching financial data for {request.user.email}: {str(e)}", exc_info=True)
            return Response(
                {'detail': _('An error occurred while fetching financial data.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvestorPipelineListView(APIView):
    """
    Get all investors in the pipeline for the authenticated startup user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.STARTUP:
                return Response(
                    {'detail': _('This endpoint is only for startup users.')},
                    status=status.HTTP_403_FORBIDDEN
                )

            startup = Startup.objects.filter(profile=profile).first()
            if not startup:
                return Response([], status=status.HTTP_200_OK)

            investors = InvestorPipeline.objects.filter(startup=startup).order_by('-created')
            serializer = InvestorPipelineSerializer(investors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching investor pipeline for {request.user.email}: {str(e)}", exc_info=True)
            return Response(
                {'detail': _('An error occurred while fetching investor pipeline.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
