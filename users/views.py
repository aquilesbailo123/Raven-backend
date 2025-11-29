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
from users.models import Startup, Profile
from users.serializers.startup import StartupOnboardingSerializer, StartupSerializer

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
