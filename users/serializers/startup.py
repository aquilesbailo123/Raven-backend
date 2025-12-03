from rest_framework import serializers
from users.models import Startup, Evidence, FinancialInput, InvestorPipeline, Round
from django.db.models import Max, Sum


class StartupSerializer(serializers.ModelSerializer):
    """Serializer for Startup model"""

    current_trl = serializers.SerializerMethodField()
    current_crl = serializers.SerializerMethodField()
    actual_revenue = serializers.SerializerMethodField()

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
            'current_trl',
            'current_crl',
            'actual_revenue',
        )
        read_only_fields = ('id', 'created', 'updated')

    def get_current_trl(self, obj: Startup) -> int | None:
        """
        Returns the maximum TRL level from the startup's evidences.
        """
        trl_evidence = obj.evidences.filter(type='TRL').aggregate(max_level=Max('level'))
        return trl_evidence['max_level']

    def get_current_crl(self, obj: Startup) -> int | None:
        """
        Returns the maximum CRL level from the startup's evidences.
        """
        crl_evidence = obj.evidences.filter(type='CRL').aggregate(max_level=Max('level'))
        return crl_evidence['max_level']

    def get_actual_revenue(self, obj: Startup) -> float | None:
        """
        Calculates the sum of all revenues from the startup's financial inputs.
        """
        revenue_sum = obj.financial_inputs.aggregate(total_revenue=Sum('revenue'))
        return revenue_sum['total_revenue']


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


class RoundSerializer(serializers.ModelSerializer):
    """Serializer for Round model"""
    class Meta:
        model = Round
        fields = (
            'id',
            'startup',
            'name',
            'target_amount',
            'raised_amount',
            'is_open',
            'start_date',
            'end_date',
            'notes',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'startup', 'created', 'updated')