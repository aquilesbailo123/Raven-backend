from rest_framework import serializers
from users.models import Evidence, ReadinessLevel

class PortfolioEvidenceSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and reviewing evidences from portfolio startups.
    """
    startup_id = serializers.IntegerField(source='startup.id', read_only=True)
    startup_name = serializers.CharField(source='startup.company_name', read_only=True)
    startup_logo = serializers.URLField(source='startup.logo_url', read_only=True)
    
    class Meta:
        model = Evidence
        fields = (
            'id', 'startup_id', 'startup_name', 'startup_logo',
            'type', 'level', 'description', 'file_url',
            'status', 'reviewer_notes', 'created', 'updated'
        )
        read_only_fields = ('id', 'startup_id', 'startup_name', 'startup_logo', 
                           'type', 'level', 'description', 'file_url', 'created', 'updated')


class EvidenceReviewSerializer(serializers.Serializer):
    """
    Serializer for reviewing (approving/rejecting) an evidence.
    """
    status = serializers.ChoiceField(choices=['PENDING', 'APPROVED', 'REJECTED'])
    reviewer_notes = serializers.CharField(required=False, allow_blank=True)


class PortfolioReadinessLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing readiness levels from portfolio startups.
    """
    startup_id = serializers.IntegerField(source='startup.id', read_only=True)
    startup_name = serializers.CharField(source='startup.company_name', read_only=True)
    evidences = serializers.SerializerMethodField()

    class Meta:
        model = ReadinessLevel
        fields = (
            'id', 'startup_id', 'startup_name',
            'type', 'level', 'title', 'subtitle',
            'evidences', 'created', 'updated'
        )
        read_only_fields = fields

    def get_evidences(self, obj):
        # Get evidences for this specific level and type
        evidences = Evidence.objects.filter(
            startup=obj.startup,
            type=obj.type,
            level=obj.level
        )
        return PortfolioEvidenceSerializer(evidences, many=True).data


class PortfolioCampaignSerializer(serializers.Serializer):
    """
    Serializer for viewing campaigns from portfolio startups.
    """
    startup_id = serializers.IntegerField()
    startup_name = serializers.CharField()
    startup_logo = serializers.URLField(allow_null=True)
    industry = serializers.CharField(allow_null=True)
    trl_level = serializers.IntegerField()
    crl_level = serializers.IntegerField()
    campaign = serializers.SerializerMethodField()

    def get_campaign(self, obj):
        from campaigns.serializers import CampaignSerializer
        if hasattr(obj, 'campaign'):
            return CampaignSerializer(obj.campaign).data
        return None
