from rest_framework import serializers
from users.models import Startup, Evidence, FinancialInput, InvestorPipeline, Round
from django.db.models import Max, Sum


from users.serializers.incubator import IncubatorSerializer

class StartupSerializer(serializers.ModelSerializer):
    """Serializer for Startup model"""

    actual_revenue = serializers.SerializerMethodField()
    incubators = IncubatorSerializer(many=True, read_only=True)

    class Meta:
        model = Startup
        fields = (
            'id',
            'company_name',
            'industry',
            'logo_url',
            'TRL_level',
            'CRL_level',
            'created',
            'updated',
            'actual_revenue',
            'incubators',
        )
        read_only_fields = ('id', 'created', 'updated', 'TRL_level', 'CRL_level')

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
        fields = ('company_name', 'industry', 'TRL_level', 'CRL_level')

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


class EvidenceSerializer(serializers.ModelSerializer):
    """
    Serializer for Evidence data.
    Each evidence is EITHER TRL OR CRL, not both.
    """
    class Meta:
        model = Evidence
        fields = (
            'id',
            'type',
            'level',
            'description',
            'file_url',
            'status',
            'reviewer_notes',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'status', 'created', 'updated')

    def validate_type(self, value):
        if value not in ['TRL', 'CRL']:
            raise serializers.ValidationError("Evidence type must be 'TRL' or 'CRL'")
        return value

    def validate_level(self, value):
        if value < 1 or value > 9:
            raise serializers.ValidationError("Level must be between 1 and 9")
        return value


class FinancialInputSerializer(serializers.ModelSerializer):
    """Serializer for Financial Input data"""
    net_cash_flow = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True,
        help_text="Calculated net cash flow (revenue - costs)"
    )

    class Meta:
        model = FinancialInput
        fields = (
            'id',
            'period_date',
            'revenue',
            'costs',
            'cash_balance',
            'monthly_burn',
            'net_cash_flow',
            'notes',
            'created',
        )
        read_only_fields = ('id', 'net_cash_flow', 'created')

    def validate_revenue(self, value):
        if value < 0:
            raise serializers.ValidationError("Revenue cannot be negative")
        return value

    def validate_costs(self, value):
        if value < 0:
            raise serializers.ValidationError("Costs cannot be negative")
        return value


class InvestorPipelineSerializer(serializers.ModelSerializer):
    """Serializer for Investor Pipeline data"""
    class Meta:
        model = InvestorPipeline
        fields = (
            'id',
            'investor_name',
            'investor_email',
            'stage',
            'ticket_size',
            'notes',
            'next_action_date',
            'created',
        )
        read_only_fields = ('id', 'created')

    def validate_investor_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Investor name cannot be empty")
        return value.strip()