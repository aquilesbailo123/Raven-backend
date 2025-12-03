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