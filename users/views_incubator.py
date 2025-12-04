from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from users.models import Incubator, IncubatorMember, Challenge, ChallengeApplication, Profile, Startup
from users.serializers.incubator import (
    IncubatorSerializer,
    IncubatorMemberSerializer,
    ChallengeSerializer,
    ChallengeApplicationSerializer,
    StartupIncubatorAssociationSerializer
)
from users.serializers.startup import StartupSerializer

class IncubatorViewSet(viewsets.ModelViewSet):
    """
    CRUD for Incubator profiles.
    Also provides endpoints to see associated startups.
    """
    queryset = Incubator.objects.all()
    serializer_class = IncubatorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # If user is incubator, show their own profile primarily
        # But we might want to list all incubators for Startups to choose from
        if self.action == 'list':
            return Incubator.objects.all()
        return Incubator.objects.all()

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        Get consolidated data for the incubator, including portfolio startups.
        """
        incubator = self.get_object()
        serializer = self.get_serializer(incubator)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def startups(self, request, pk=None):
        """
        Get all startups associated with this incubator.
        Only the incubator owner should ideally see detailed metrics, 
        but for now we allow authenticated users (or restrict to owner).
        """
        incubator = self.get_object()
        
        # Security check: Only allow the incubator owner to see their startups' detailed metrics?
        # Requirement: "una incuvator puede ver todas sus startup asociadas y las métricas de cada uno"
        if request.user.profile.user_type == Profile.INCUBATOR and request.user.profile.incubator != incubator:
             return Response({"detail": "Not authorized to view another incubator's startups."}, status=status.HTTP_403_FORBIDDEN)

        startups = incubator.startups.all()
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_all(self, request):
        """
        Get all incubators.
        If the user is a startup, it filters out the incubators that are already associated.
        """
        user_profile = request.user.profile
        queryset = Incubator.objects.all()

        if user_profile.user_type == Profile.STARTUP:
            try:
                startup = user_profile.startup
                associated_incubator_ids = startup.incubators.values_list('id', flat=True)
                queryset = queryset.exclude(id__in=associated_incubator_ids)
            except Startup.DoesNotExist:
                # Startup profile exists but startup object doesn't, so no associations to exclude
                pass

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IncubatorMemberViewSet(viewsets.ModelViewSet):
    """
    Manage Investors and Mentors for an Incubator.
    """
    serializer_class = IncubatorMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return members of the current user's incubator
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == Profile.INCUBATOR:
             return IncubatorMember.objects.filter(incubator=self.request.user.profile.incubator)
        return IncubatorMember.objects.none()

    def perform_create(self, serializer):
        if self.request.user.profile.user_type != Profile.INCUBATOR:
            raise serializers.ValidationError("Only incubators can add members.")
        serializer.save(incubator=self.request.user.profile.incubator)


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    Manage Challenges.
    Incubators create/edit. Startups view.
    """
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Incubators see their own challenges. Startups see all OPEN challenges?
        # Or maybe everyone sees all challenges?
        # Requirement: "cada incuvator puede lanzar desafios"
        user_profile = self.request.user.profile
        if user_profile.user_type == Profile.INCUBATOR:
            return Challenge.objects.filter(incubator=user_profile.incubator)
        elif user_profile.user_type == Profile.STARTUP:
            return Challenge.objects.filter(status=Challenge.OPEN) # Startups usually see open challenges
        return Challenge.objects.none()

    def perform_create(self, serializer):
        if self.request.user.profile.user_type != Profile.INCUBATOR:
            raise serializers.ValidationError("Only incubators can create challenges.")
        serializer.save(incubator=self.request.user.profile.incubator)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a challenge"""
        challenge = self.get_object()
        if request.user.profile.incubator != challenge.incubator:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        challenge.status = Challenge.CONCLUDED
        challenge.save()
        return Response({"status": "Challenge concluded"})


class ChallengeApplicationViewSet(viewsets.ModelViewSet):
    """
    Startups apply to challenges.
    Incubators view applications for their challenges.
    """
    serializer_class = ChallengeApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.profile
        if user_profile.user_type == Profile.STARTUP:
            return ChallengeApplication.objects.filter(startup=user_profile.startup)
        elif user_profile.user_type == Profile.INCUBATOR:
            return ChallengeApplication.objects.filter(challenge__incubator=user_profile.incubator)
        return ChallengeApplication.objects.none()

    def perform_create(self, serializer):
        if self.request.user.profile.user_type != Profile.STARTUP:
            raise serializers.ValidationError("Only startups can apply to challenges.")
        serializer.save(startup=self.request.user.profile.startup)


class StartupIncubatorAssociationViewSet(viewsets.ViewSet):
    """
    Endpoint for Startups to select/deselect Incubators.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = IncubatorSerializer # Add serializer class for swagger documentation

    def list(self, request):
        """
        List all incubators associated with the current startup.
        """
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != Profile.STARTUP:
            return Response({"detail": "Only startups can perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            startup = request.user.profile.startup
            associated_incubators = startup.incubators.all()
            serializer = self.serializer_class(associated_incubators, many=True)
            return Response(serializer.data)
        except Startup.DoesNotExist:
            return Response({"detail": "Startup profile not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def associate(self, request):
        """
        Set the list of incubators the startup is associated with.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Received incubator association request with data: {request.data}")

        if not hasattr(request.user, 'profile') or request.user.profile.user_type != Profile.STARTUP:
            return Response({"detail": "Only startups can perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = StartupIncubatorAssociationSerializer(data=request.data)
        if serializer.is_valid():
            incubator_ids = serializer.validated_data['incubator_ids']
            
            try:
                startup = request.user.profile.startup
            except Startup.DoesNotExist:
                return Response({"detail": "Startup profile not found."}, status=status.HTTP_404_NOT_FOUND)

            logger.info(f"Attempting to associate startup {startup.id} with incubator IDs: {incubator_ids}")

            # Verify incubators exist
            incubators = Incubator.objects.filter(id__in=incubator_ids)
            if len(incubators) != len(incubator_ids):
                 return Response({"detail": "One or more Incubator IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)

            # Set the relationship (replace existing)
            startup.incubators.set(incubators)
            
            logger.info(f"Successfully associated startup {startup.id} with incubators: {[i.id for i in incubators]}")

            # Return the updated list of associated incubators
            updated_incubators = startup.incubators.all()
            response_serializer = self.serializer_class(updated_incubators, many=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from campaigns.models import Investor
from users.serializers.investment import IncubatorInvestmentSerializer, IncubatorInvestmentUpdateSerializer

class IncubatorInvestmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Manage Investments (Deals) for an Incubator.
    Allows viewing all investments and updating their status.
    """
    serializer_class = IncubatorInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return investments associated with the current user's incubator
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == Profile.INCUBATOR:
             return Investor.objects.filter(incubator=self.request.user.profile.incubator).select_related(
                 'round', 'round__campaign__startup'
             )
        return Investor.objects.none()

    @action(detail=True, methods=['post'])
    def commit(self, request, pk=None):
        """
        Change the status of an investment to COMMITTED.
        """
        investment = self.get_object()
        
        # Verify the investment belongs to the current incubator
        if investment.incubator != request.user.profile.incubator:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        investment.status = Investor.Status.COMMITTED
        investment.save()
        
        serializer = self.get_serializer(investment)
        return Response(serializer.data)


from users.models import Evidence, ReadinessLevel
from users.serializers.portfolio import (
    PortfolioEvidenceSerializer, 
    EvidenceReviewSerializer,
    PortfolioReadinessLevelSerializer
)

class PortfolioEvidenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View and review evidences from portfolio startups.
    Only accessible by incubators.
    """
    serializer_class = PortfolioEvidenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all evidences from startups associated with this incubator
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == Profile.INCUBATOR:
            incubator = self.request.user.profile.incubator
            # Get all startup IDs associated with this incubator
            startup_ids = incubator.startups.values_list('id', flat=True)
            return Evidence.objects.filter(startup_id__in=startup_ids).select_related('startup')
        return Evidence.objects.none()

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Approve or reject an evidence.
        """
        evidence = self.get_object()
        
        # Verify the evidence's startup belongs to this incubator
        incubator = request.user.profile.incubator
        if evidence.startup not in incubator.startups.all():
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EvidenceReviewSerializer(data=request.data)
        if serializer.is_valid():
            evidence.status = serializer.validated_data['status']
            evidence.reviewer_notes = serializer.validated_data.get('reviewer_notes', '')
            evidence.save()
            
            # If approved and this is the highest level, update startup's TRL/CRL
            if evidence.status == 'APPROVED':
                self._update_startup_level(evidence)
            
            return Response(PortfolioEvidenceSerializer(evidence).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _update_startup_level(self, evidence):
        """
        Update the startup's TRL/CRL level if this evidence is for a higher level.
        """
        startup = evidence.startup
        if evidence.type == 'TRL':
            if evidence.level > startup.TRL_level:
                startup.TRL_level = evidence.level
                startup.save(update_fields=['TRL_level'])
        elif evidence.type == 'CRL':
            if evidence.level > startup.CRL_level:
                startup.CRL_level = evidence.level
                startup.save(update_fields=['CRL_level'])


class PortfolioReadinessLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View readiness levels from portfolio startups (with nested evidences).
    Only accessible by incubators.
    """
    serializer_class = PortfolioReadinessLevelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all readiness levels from startups associated with this incubator
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == Profile.INCUBATOR:
            incubator = self.request.user.profile.incubator
            startup_ids = incubator.startups.values_list('id', flat=True)
            return ReadinessLevel.objects.filter(startup_id__in=startup_ids).select_related('startup')
        return ReadinessLevel.objects.none()


from users.serializers.portfolio import PortfolioCampaignSerializer

class PortfolioCampaignViewSet(viewsets.ViewSet):
    """
    View campaigns and metrics from all portfolio startups.
    Only accessible by incubators.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all campaigns from portfolio startups with their metrics.
        """
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != Profile.INCUBATOR:
            return Response({"detail": "Only incubators can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)
        
        incubator = request.user.profile.incubator
        startups = incubator.startups.select_related('campaign', 'campaign__financials').prefetch_related(
            'campaign__rounds', 
            'campaign__rounds__investors'
        ).all()
        
        # Build response data
        data = []
        for startup in startups:
            startup_data = {
                'startup_id': startup.id,
                'startup_name': startup.company_name,
                'startup_logo': startup.logo_url,
                'industry': startup.industry,
                'trl_level': startup.TRL_level,
                'crl_level': startup.CRL_level,
                'campaign': None
            }
            
            if hasattr(startup, 'campaign'):
                from campaigns.serializers import CampaignSerializer
                startup_data['campaign'] = CampaignSerializer(startup.campaign).data
            
            data.append(startup_data)
        
        return Response(data)

from rest_framework.views import APIView
from users.serializers.incubator import IncubatorOnboardingSerializer

class IncubatorOnboardingView(APIView):
    """
    API endpoint for incubator onboarding.
    Allows authenticated incubator users to complete their profile.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.INCUBATOR:
                return Response(
                    {'detail': 'This endpoint is only for incubator users.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create incubator
            incubator, created = Incubator.objects.get_or_create(
                profile=profile,
                defaults={'name': ''}
            )

            serializer = IncubatorOnboardingSerializer(incubator, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save(profile_complete=True)

            return Response({
                'detail': 'Onboarding completed successfully.',
                'incubator': IncubatorSerializer(incubator).data
            }, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

class IncubatorDataView(APIView):
    """
    API endpoint to retrieve the current incubator's data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            if profile.user_type != Profile.INCUBATOR:
                return Response(
                    {'detail': 'This endpoint is only for incubator users.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create incubator
            # This ensures that even if the user hasn't completed onboarding,
            # they have an incubator instance to work with.
            # We provide a default name because the field is required in the model.
            incubator, created = Incubator.objects.get_or_create(
                profile=profile,
                defaults={'name': ''}
            )

            serializer = IncubatorSerializer(incubator)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
