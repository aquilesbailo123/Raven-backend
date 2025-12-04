from rest_framework import serializers
from campaigns.models import Investor, InvestmentRound

class IncubatorInvestmentSerializer(serializers.ModelSerializer):
    """
    Serializer for listing investments made by an incubator.
    Includes details about the round and the startup.
    """
    round_name = serializers.CharField(source='round.name', read_only=True)
    startup_name = serializers.CharField(source='round.campaign.startup.company_name', read_only=True)
    startup_id = serializers.IntegerField(source='round.campaign.startup.id', read_only=True)
    logo_url = serializers.URLField(source='round.campaign.startup.logo_url', read_only=True)
    
    class Meta:
        model = Investor
        fields = (
            'id', 'round', 'round_name', 'startup_id', 'startup_name', 'logo_url', 
            'amount', 'status', 'created', 'updated'
        )
        read_only_fields = ('id', 'round', 'created', 'updated', 'amount') # Amount usually set by startup or negotiation? Or should be writable? Assuming read-only for now unless specified.

class IncubatorInvestmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the status of an investment.
    """
    class Meta:
        model = Investor
        fields = ('status',)
