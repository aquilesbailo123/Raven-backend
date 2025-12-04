from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Campaign
from .serializers import CampaignSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Campaign applications.
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own startup's campaign.
        """
        try:
            startup = self.request.user.profile.startup
            return self.queryset.filter(startup=startup)
        except AttributeError:
            # Handle cases where user has no profile or startup
            return self.queryset.none()

    @action(detail=False, methods=['get'], url_path='my-campaign')
    def my_campaign(self, request):
        """
        Get the active campaign for the current user's startup.
        If the startup or campaign don't exist, they are created.
        """
        try:
            profile = request.user.profile
        except AttributeError:
            # This happens if a user is authenticated but has no profile object.
            # This should ideally be handled during registration.
            return Response(
                {"detail": "User has no associated profile."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Import here to avoid circular dependency issues
        from users.models import Startup
        
        # Get or create the Startup instance for the user's profile
        startup, startup_created = Startup.objects.get_or_create(profile=profile)

        campaign, campaign_created = Campaign.objects.get_or_create(
            startup=startup,
            defaults={'status': Campaign.Status.DRAFT}
        )
        
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Associate the campaign with the user's startup.
        If the startup doesn't exist, it is created.
        """
        try:
            profile = self.request.user.profile
            from users.models import Startup
            startup, _ = Startup.objects.get_or_create(profile=profile)
            serializer.save(startup=startup)
        except AttributeError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User has no associated profile.")


    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit the campaign application.
        This changes the status to SUBMITTED.
        """
        campaign = self.get_object()
        
        # Add validation logic here to ensure campaign is complete
        # For now, we just change the status
        
        if campaign.status != Campaign.Status.DRAFT:
            return Response(
                {"detail": "This campaign has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = Campaign.Status.SUBMITTED
        campaign.save(update_fields=['status'])
        
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='financials')
    def financials(self, request, pk=None):
        """
        Get or update the financials for a campaign.
        GET: Returns the CampaignFinancials object.
        PATCH: Updates the CampaignFinancials object.
        """
        campaign = self.get_object()
        
        # Get or create the financials object
        from .models import CampaignFinancials
        financials, created = CampaignFinancials.objects.get_or_create(campaign=campaign)
        
        if request.method == 'GET':
            from .serializers import CampaignFinancialsSerializer
            serializer = CampaignFinancialsSerializer(financials)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            from .serializers import CampaignFinancialsSerializer
            serializer = CampaignFinancialsSerializer(financials, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='startup/(?P<startup_id>[^/.]+)')
    def by_startup(self, request, startup_id=None):
        """
        Get the campaign for a specific startup.
        Used by incubators to view portfolio startup campaigns.
        """
        from users.models import Startup, Profile
        
        # Check if user is an incubator
        if not hasattr(request.user, 'profile'):
            return Response({"detail": "User has no profile."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            startup = Startup.objects.get(pk=startup_id)
        except Startup.DoesNotExist:
            return Response({"detail": "Startup not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # If user is incubator, check if startup is in their portfolio
        if request.user.profile.user_type == Profile.INCUBATOR:
            incubator = request.user.profile.incubator
            if startup not in incubator.startups.all():
                return Response({"detail": "Startup not in your portfolio."}, status=status.HTTP_403_FORBIDDEN)
        # If user is startup, they can only view their own campaign
        elif request.user.profile.user_type == Profile.STARTUP:
            if request.user.profile.startup != startup:
                return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create campaign for the startup
        campaign, created = Campaign.objects.get_or_create(
            startup=startup,
            defaults={'status': Campaign.Status.DRAFT}
        )
        
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)


from .models import InvestmentRound
from .serializers import InvestmentRoundSerializer

class RoundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Investment Rounds and their nested Investors.
    """
    queryset = InvestmentRound.objects.all()
    serializer_class = InvestmentRoundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see rounds for their own startup's campaign.
        """
        try:
            startup = self.request.user.profile.startup
            # Assuming Campaign is linked to Startup via OneToOne 'campaign'
            # and InvestmentRound is linked to Campaign via ForeignKey 'campaign'
            if hasattr(startup, 'campaign'):
                return self.queryset.filter(campaign=startup.campaign)
            return self.queryset.none()
        except AttributeError:
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        Associate the round with the user's startup campaign.
        """
        try:
            startup = self.request.user.profile.startup
            if not hasattr(startup, 'campaign'):
                 # Create campaign if it doesn't exist (optional, but good for safety)
                 from .models import Campaign
                 Campaign.objects.create(startup=startup)
            
            serializer.save(campaign=startup.campaign)
        except AttributeError:
             from rest_framework.exceptions import ValidationError
             raise ValidationError("User has no associated profile or startup.")