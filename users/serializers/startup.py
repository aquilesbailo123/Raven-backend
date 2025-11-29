from rest_framework import serializers
from users.models import Startup


class StartupSerializer(serializers.ModelSerializer):
    """Serializer for Startup model"""

    class Meta:
        model = Startup
        fields = (
            'id',
            'company_name',
            'industry',
            'logo_url',
            'is_mock_data',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')


class StartupOnboardingSerializer(serializers.ModelSerializer):
    """Serializer for Startup onboarding - only company_name and industry"""

    class Meta:
        model = Startup
        fields = ('company_name', 'industry')

    def validate_company_name(self, value):
        """Validate company name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Company name cannot be empty")
        return value.strip()

    def validate_industry(self, value):
        """Validate industry is not empty"""
        if not value:
            raise serializers.ValidationError("Industry must be selected")
        return value
