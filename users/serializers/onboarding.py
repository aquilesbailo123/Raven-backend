"""
Onboarding Wizard Serializers - Phase 2
Complete nested serializer for multi-step onboarding form
"""
from rest_framework import serializers
from django.db import transaction
from users.models import Evidence, FinancialInput, InvestorPipeline, Startup
from campaigns.models import Campaign, CampaignFinancials


class EvidenceSerializer(serializers.ModelSerializer):
    """
    Serializer for Evidence data in onboarding wizard.

    Each evidence is EITHER TRL OR CRL, not both.
    Uses evidence_type and level fields (new structure).
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
        """Validate evidence type is TRL or CRL"""
        if value not in ['TRL', 'CRL']:
            raise serializers.ValidationError("Evidence type must be 'TRL' or 'CRL'")
        return value

    def validate_level(self, value):
        """Validate level is between 1 and 9"""
        if value < 1 or value > 9:
            raise serializers.ValidationError("Level must be between 1 and 9")
        return value

class FinancialInputSerializer(serializers.ModelSerializer):
    """Serializer for Financial Input data in onboarding wizard"""

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
        """Validate revenue is not negative"""
        if value < 0:
            raise serializers.ValidationError("Revenue cannot be negative")
        return value

    def validate_costs(self, value):
        """Validate costs is not negative"""
        if value < 0:
            raise serializers.ValidationError("Costs cannot be negative")
        return value

    def validate_cash_balance(self, value):
        """Cash balance can be negative (debt), but warn if too negative"""
        if value < -1000000:  # Less than -$1M
            raise serializers.ValidationError(
                "Cash balance seems unrealistically negative. Please verify."
            )
        return value

    def validate_monthly_burn(self, value):
        """Validate monthly burn is not negative"""
        if value < 0:
            raise serializers.ValidationError("Monthly burn rate cannot be negative")
        return value


class InvestorPipelineSerializer(serializers.ModelSerializer):
    """Serializer for Investor Pipeline data in onboarding wizard"""

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
        """Validate investor name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Investor name cannot be empty")
        return value.strip()

    def validate_ticket_size(self, value):
        """Validate ticket size is positive if provided"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Ticket size must be greater than 0")
        return value


class OnboardingWizardSerializer(serializers.Serializer):
    """
    Main nested serializer for complete onboarding wizard.
    Receives all data from the multi-step form in a single POST request.

    Expected structure:
    {
        "company_name": "My Startup",
        "industry": "fintech",
        "current_trl": 3,
        "target_funding_amount": 150000.00,
        "evidences": [
            {
                "trl_level": 3,
                "description": "Proof of concept completed",
                "file": <file> or "file_url": "https://..."
            }
        ],
        "financial_data": [
            {
                "period_date": "2024-01-31",
                "revenue": 5000.00,
                "costs": 8000.00,
                "cash_balance": 45000.00,
                "monthly_burn": 3000.00
            },
            ...
        ],
        "investors": [
            {
                "investor_name": "Angel Investor 1",
                "investor_email": "investor@example.com",
                "stage": "CONTACTED",
                "ticket_size": 50000.00
            },
            ...
        ]
    }
    """

    # Step 0: Company basics
    company_name = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=False,
        help_text="Company/Startup name"
    )
    industry = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        help_text="Industry sector (must match choices: technology, fintech, healthtech, etc.)"
    )

    # Step 1: TRL/CRL Progress
    current_trl = serializers.IntegerField(
        min_value=1,
        max_value=9,
        help_text="Current Technology Readiness Level (1-9)"
    )
    current_crl = serializers.IntegerField(
        min_value=1,
        max_value=9,
        required=False,
        allow_null=True,
        help_text="Current Commercial Readiness Level (1-9)"
    )
    evidences = EvidenceSerializer(many=True, required=True)

    # Step 2: Financial Data
    financial_data = FinancialInputSerializer(many=True, required=True)
    financial_projections = serializers.JSONField(
        required=True,
        help_text="Quarterly financial projections (revenue, COGS, OPEX)"
    )

    # Step 3: Investors
    target_funding_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        help_text="Target amount for current funding round"
    )
    investors = InvestorPipelineSerializer(many=True, required=True)

    def validate_evidences(self, value):
        """Allow evidences to be optional. Other validations will apply if evidences are provided."""
        return value

    def validate_financial_data(self, value):
        """Validate that at least one financial period is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "At least one financial period must be provided"
            )

        # Check for duplicate periods
        periods = [item['period_date'] for item in value]
        if len(periods) != len(set(periods)):
            raise serializers.ValidationError(
                "Duplicate period dates found in financial data"
            )

        return value

    def validate_investors(self, value):
        """Validate that at least one investor is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "At least one investor must be provided"
            )
        return value

    def validate(self, data):
        """
        Cross-field validation for TRL/CRL evidences.

        Rules:
        - At least one TRL evidence matching current_trl
        - If current_crl provided, at least one CRL evidence matching it
        """
        current_trl = data.get('current_trl')
        current_crl = data.get('current_crl')
        evidences = data.get('evidences', [])

        # Separate evidences by type
        trl_evidences = [e for e in evidences if e.get('type') == 'TRL']
        crl_evidences = [e for e in evidences if e.get('type') == 'CRL']

        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Validation: current_trl={current_trl}, current_crl={current_crl}")
        logger.debug(f"Validation: evidences={evidences}")
        logger.debug(f"Validation: trl_evidences={trl_evidences}")

        # Validate TRL evidence exists for current_trl
        has_matching_trl = any(
            evidence.get('level') <= current_trl
            for evidence in trl_evidences
        )
        logger.debug(f"Validation: has_matching_trl={has_matching_trl}")

        if not has_matching_trl:
            raise serializers.ValidationError({
                'evidences': f'At least one TRL evidence must be provided for your current TRL level ({current_trl})'
            })

        # Validate CRL evidence if current_crl is provided
        if current_crl is not None:
            has_matching_crl = any(
                evidence.get('level') <= current_crl
                for evidence in crl_evidences
            )

            if not has_matching_crl:
                raise serializers.ValidationError({
                    'evidences': f'At least one CRL evidence must be provided for your current CRL level ({current_crl})'
                })

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create all onboarding data and update startup.
        This method handles:
        1. Deleting all mock data for the startup
        2. Creating real data from the wizard
        3. Updating startup.is_mock_data to False
        """
        # Get startup from context (passed from view)
        startup = self.context.get('startup')
        if not startup:
            raise serializers.ValidationError("Startup not found in context")

        # Extract nested data
        company_name = validated_data.pop('company_name')
        industry = validated_data.pop('industry')
        evidences_data = validated_data.pop('evidences')
        financial_data = validated_data.pop('financial_data')
        investors_data = validated_data.pop('investors')
        current_trl = validated_data.pop('current_trl')
        current_crl = validated_data.pop('current_crl', None)
        target_funding_amount = validated_data.pop('target_funding_amount')

        # Extract financial_projections separately, as it belongs to CampaignFinancials
        financial_projections_data = validated_data.pop('financial_projections')

        # =====================================================================
        # STEP 1: DELETE ALL MOCK DATA
        # =====================================================================
        # Delete all existing data that was created during seeding
        Evidence.objects.filter(startup=startup).delete()
        FinancialInput.objects.filter(startup=startup).delete()
        InvestorPipeline.objects.filter(startup=startup).delete()

        # =====================================================================
        # STEP 2: CREATE REAL DATA
        # =====================================================================

        # Create evidences
        created_evidences = []
        for evidence_data in evidences_data:
            evidence = Evidence.objects.create(
                startup=startup,
                **evidence_data
            )
            created_evidences.append(evidence)

        # Create financial inputs
        created_financial_inputs = []
        for financial_input_data in financial_data:
            financial_input = FinancialInput.objects.create(
                startup=startup,
                **financial_input_data
            )
            created_financial_inputs.append(financial_input)

        # Create investor pipeline entries
        created_investors = []
        for investor_data in investors_data:
            investor = InvestorPipeline.objects.create(
                startup=startup,
                **investor_data
            )
            created_investors.append(investor)

        # =====================================================================
        # STEP 3: UPDATE STARTUP
        # =====================================================================
        # Update startup with company data and mark onboarding as complete
        startup.company_name = company_name
        startup.industry = industry
        startup.is_mock_data = False
        startup.onboarding_completed = True  # MARK ONBOARDING AS COMPLETE
        startup.save(update_fields=[
            'company_name',
            'industry',
            'is_mock_data',
            'onboarding_completed',
            'updated'
        ])

        # Retrieve or create Campaign and CampaignFinancials
        campaign, created = Campaign.objects.get_or_create(startup=startup)
        campaign_financials, created = CampaignFinancials.objects.get_or_create(campaign=campaign)
        campaign_financials.financial_projections = financial_projections_data
        campaign_financials.save(update_fields=['financial_projections'])

        # Return aggregated data
        return {
            'startup': startup,
            'current_trl': current_trl,
            'current_crl': current_crl,
            'target_funding_amount': target_funding_amount,
            'evidences': created_evidences,
            'financial_data': created_financial_inputs,
            'investors': created_investors,
        }

    def to_representation(self, instance):
        """Custom representation for the created data"""
        result = {
            'detail': 'Onboarding wizard completed successfully',
            'startup_id': instance['startup'].id,
            'is_mock_data': instance['startup'].is_mock_data,
            'current_trl': instance['current_trl'],
            'target_funding_amount': str(instance['target_funding_amount']),
            'evidences_count': len(instance['evidences']),
            'financial_periods_count': len(instance['financial_data']),
            'investors_count': len(instance['investors']),
        }

        # Add current_crl if it exists
        if instance.get('current_crl') is not None:
            result['current_crl'] = instance['current_crl']

        return result
