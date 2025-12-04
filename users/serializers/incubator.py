from rest_framework import serializers
from users.models import Incubator, IncubatorMember, Challenge, ChallengeApplication, Startup

class IncubatorMemberSerializer(serializers.ModelSerializer):
    """Serializer for Incubator Members (Investors/Mentors)"""
    class Meta:
        model = IncubatorMember
        fields = ('id', 'incubator', 'full_name', 'email', 'phone', 'role', 'created', 'updated')
        read_only_fields = ('id', 'incubator', 'created', 'updated')


class AssociatedStartupSerializer(serializers.ModelSerializer):
    """Simple serializer for listing associated startups"""
    class Meta:
        model = Startup
        fields = ('id', 'company_name', 'logo_url', 'industry')
        read_only_fields = ('id', 'company_name', 'logo_url', 'industry')


class IncubatorSerializer(serializers.ModelSerializer):
    """Serializer for Incubator profile"""
    members = IncubatorMemberSerializer(many=True, read_only=True)
    startups = AssociatedStartupSerializer(many=True, read_only=True) # Keep this for backward compatibility if needed, or remove if portfolio_startups replaces it. The prompt says "Agregar Campo Calculado (Portafolio): Agrega un SerializerMethodField llamado portfolio_startups".
    portfolio_summary = serializers.SerializerMethodField()
    portfolio_startups = serializers.SerializerMethodField()

    class Meta:
        model = Incubator
        fields = ('id', 'name', 'description', 'logo_url', 'profile_complete', 'members', 'startups', 'portfolio_startups', 'portfolio_summary', 'created', 'updated')
        read_only_fields = ('id', 'created', 'updated')

    def get_portfolio_startups(self, obj):
        """
        Returns the list of all startups associated with this incubator.
        """
        startups = obj.startups.all()
        return AssociatedStartupSerializer(startups, many=True).data

    def get_portfolio_summary(self, obj):
        """
        Calculates aggregated metrics for the incubator's portfolio.
        """
        from django.db.models import Sum, Avg, F, Q
        from campaigns.models import Investor

        # Get all startups associated with this incubator
        startups = obj.startups.all()
        
        # Calculate total portfolio target (sum of funding_goal from campaign financials)
        total_target = 0
        for startup in startups:
            if hasattr(startup, 'campaign') and hasattr(startup.campaign, 'financials'):
                goal = startup.campaign.financials.funding_goal
                if goal:
                    total_target += goal

        # Calculate total portfolio committed (sum of total_capital_injection)
        # We need to sum up committed investments for all campaigns of these startups
        total_committed = 0
        for startup in startups:
            if hasattr(startup, 'campaign'):
                for inv_round in startup.campaign.rounds.all():
                    # Sum amounts of investors with status COMMITTED
                    committed_in_round = inv_round.investors.filter(status=Investor.Status.COMMITTED).aggregate(total=Sum('amount'))['total']
                    if committed_in_round:
                        total_committed += committed_in_round

        # Calculate average TRL
        avg_trl = startups.aggregate(Avg('TRL_level'))['TRL_level__avg'] or 0

        return {
            'total_portfolio_target': total_target,
            'total_portfolio_committed': total_committed,
            'average_trl': round(avg_trl, 2)
        }


class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for Challenges"""
    applicant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Challenge
        fields = (
            'id', 'incubator', 'title', 'subtitle', 'description', 
            'budget', 'deadline', 'required_technologies', 
            'status', 'applicant_count', 'created', 'updated'
        )
        read_only_fields = ('id', 'incubator', 'applicant_count', 'created', 'updated')


class ChallengeApplicationSerializer(serializers.ModelSerializer):
    """Serializer for applying to challenges"""
    startup_name = serializers.CharField(source='startup.company_name', read_only=True)

    class Meta:
        model = ChallengeApplication
        fields = ('id', 'challenge', 'startup', 'startup_name', 'text_solution', 'created', 'updated')
        read_only_fields = ('id', 'startup', 'startup_name', 'created', 'updated')


class StartupIncubatorAssociationSerializer(serializers.Serializer):
    """Serializer for Startups to select/deselect Incubators"""
    incubator_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of Incubator IDs to associate with"
    )

class IncubatorOnboardingSerializer(serializers.ModelSerializer):
    """Serializer for Incubator onboarding"""
    class Meta:
        model = Incubator
        fields = ('name', 'description', 'logo_url')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()
