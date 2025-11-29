"""
Onboarding Wizard Serializers - Phase 2
Complete nested serializer for multi-step onboarding form
"""
from rest_framework import serializers
from django.db import transaction
from users.models import Evidence, FinancialInput, InvestorPipeline, Startup


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for Evidence data in onboarding wizard"""

    class Meta:
        model = Evidence
        fields = (
            'id',
            'trl_level',
            'description',
            'file',
            'file_url',
            'status',
            'created',
        )
        read_only_fields = ('id', 'status', 'created')

    def validate_trl_level(self, value):
        """Validate TRL level is between 1 and 9"""
        if value < 1 or value > 9:
            raise serializers.ValidationError("TRL level must be between 1 and 9")
        return value

    def validate(self, data):
        """Validate that at least one file source is provided"""
        if not data.get('file') and not data.get('file_url'):
            raise serializers.ValidationError({
                'file': 'Either file upload or file_url must be provided'
            })
        return data


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
    evidences = EvidenceSerializer(many=True, required=True)

    # Step 2: Financial Data
    financial_data = FinancialInputSerializer(many=True, required=True)

    # Step 3: Investors
    target_funding_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        help_text="Target amount for current funding round"
    )
    investors = InvestorPipelineSerializer(many=True, required=True)

    def validate_evidences(self, value):
        """Validate that at least one evidence is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "At least one evidence document must be provided"
            )
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
        """Cross-field validation"""
        # Validate that current_trl matches at least one evidence
        current_trl = data.get('current_trl')
        evidences = data.get('evidences', [])

        has_matching_evidence = any(
            evidence.get('trl_level') == current_trl
            for evidence in evidences
        )

        if not has_matching_evidence:
            raise serializers.ValidationError({
                'evidences': f'At least one evidence must be provided for your current TRL level ({current_trl})'
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
        target_funding_amount = validated_data.pop('target_funding_amount')

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
        startup.save(update_fields=['company_name', 'industry', 'is_mock_data', 'onboarding_completed', 'updated'])

        # Return aggregated data
        return {
            'startup': startup,
            'current_trl': current_trl,
            'target_funding_amount': target_funding_amount,
            'evidences': created_evidences,
            'financial_data': created_financial_inputs,
            'investors': created_investors,
        }

    def to_representation(self, instance):
        """Custom representation for the created data"""
        return {
            'detail': 'Onboarding wizard completed successfully',
            'startup_id': instance['startup'].id,
            'is_mock_data': instance['startup'].is_mock_data,
            'current_trl': instance['current_trl'],
            'target_funding_amount': str(instance['target_funding_amount']),
            'evidences_count': len(instance['evidences']),
            'financial_periods_count': len(instance['financial_data']),
            'investors_count': len(instance['investors']),
        }
