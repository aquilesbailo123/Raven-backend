from django.db import transaction
from rest_framework import serializers
from users.models import Startup, Evidence, FinancialInput, InvestorPipeline
from campaigns.models import Campaign, CampaignFinancials
from .startup import EvidenceSerializer, FinancialInputSerializer, InvestorPipelineSerializer

class ReadinessLevelInputSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['TRL', 'CRL'])
    level = serializers.IntegerField(min_value=1, max_value=9)
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=255, required=False, allow_blank=True)
    evidences = EvidenceSerializer(many=True, required=False, allow_empty=True)

class OnboardingWizardSerializer(serializers.Serializer):
    """
    Serializer for the complete onboarding wizard (Phase 2).
    Handles nested creation of:
    - Readiness Levels with their Evidences
    - Incubator Association

    NOTE: Frontend now sends only completed fields. All fields except
    company_name, industry, current_trl are optional.
    """
    # Step 0: Company Basics (required)
    company_name = serializers.CharField(max_length=255, required=True)
    industry = serializers.CharField(max_length=50, required=True)

    # Step 1: TRL/CRL & Readiness Levels (TRL required, CRL and levels optional)
    current_trl = serializers.IntegerField(min_value=1, max_value=9, required=True)
    current_crl = serializers.IntegerField(min_value=1, max_value=9, required=False, allow_null=True)
    
    # New nested structure
    readiness_levels = ReadinessLevelInputSerializer(many=True, required=False, allow_empty=True)
    
    # Legacy field support (optional, can be removed if frontend fully switches)
    evidences = EvidenceSerializer(many=True, required=False, allow_empty=True)

    # Step 2: Incubators (optional)
    incubator_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )

    def validate_evidences(self, value):
        """Allow evidences to be optional."""
        return value

    def validate(self, data):
        """
        Cross-field validation.
        """
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create all onboarding data and update startup.
        """
        # Get startup from context
        startup = self.context.get('startup')
        if not startup:
            raise serializers.ValidationError("Startup not found in context")

        # Extract nested data
        company_name = validated_data.pop('company_name')
        industry = validated_data.pop('industry')
        
        readiness_levels_data = validated_data.pop('readiness_levels', [])
        legacy_evidences_data = validated_data.pop('evidences', [])
        
        incubator_ids = validated_data.pop('incubator_ids', [])
        current_trl = validated_data.pop('current_trl')
        current_crl = validated_data.pop('current_crl', None)

        # =====================================================================
        # STEP 1: DELETE ALL MOCK/OLD DATA
        # =====================================================================
        # Delete existing readiness levels (cascades to evidences linked to them)
        from users.models import ReadinessLevel
        ReadinessLevel.objects.filter(startup=startup).delete()
        # Also delete any loose evidences just in case
        Evidence.objects.filter(startup=startup).delete()

        # =====================================================================
        # STEP 2: CREATE REAL DATA
        # =====================================================================

        created_readiness_levels = []
        created_evidences = []

        # 2a. Process new structured Readiness Levels
        for rl_data in readiness_levels_data:
            evidences_data = rl_data.pop('evidences', [])
            
            # Create Readiness Level
            readiness_level = ReadinessLevel.objects.create(
                startup=startup,
                **rl_data
            )
            created_readiness_levels.append(readiness_level)

            # Create Evidences for this level
            for evidence_data in evidences_data:
                # Ensure type/level match the parent readiness level
                evidence_data['type'] = readiness_level.type
                evidence_data['level'] = readiness_level.level
                
                evidence = Evidence.objects.create(
                    startup=startup,
                    readiness_level=readiness_level,
                    **evidence_data
                )
                created_evidences.append(evidence)

        # 2b. Process legacy loose evidences (if any, for backward compatibility)
        for evidence_data in legacy_evidences_data:
            evidence = Evidence.objects.create(
                startup=startup,
                **evidence_data
            )
            created_evidences.append(evidence)

        # Associate Incubators
        if incubator_ids:
            startup.incubators.clear()
            startup.incubators.add(*incubator_ids)

        # =====================================================================
        # STEP 3: UPDATE STARTUP
        # =====================================================================
        startup.company_name = company_name
        startup.industry = industry
        startup.onboarding_completed = True
        startup.TRL_level = current_trl
        if current_crl:
            startup.CRL_level = current_crl
            
        startup.save(update_fields=[
            'company_name',
            'industry',
            'onboarding_completed',
            'TRL_level',
            'CRL_level',
            'updated'
        ])

        # Return aggregated data
        return {
            'startup': startup,
            'current_trl': current_trl,
            'current_crl': current_crl,
            'readiness_levels': created_readiness_levels,
            'evidences': created_evidences,
            'incubator_ids': incubator_ids,
        }

    def to_representation(self, instance):
        """Custom representation for the created data"""
        result = {
            'detail': 'Onboarding wizard completed successfully',
            'startup_id': instance['startup'].id,
            'current_trl': instance.get('current_trl'),
            'readiness_levels_count': len(instance.get('readiness_levels', [])),
            'evidences_count': len(instance.get('evidences', [])),
            'incubators_count': len(instance.get('incubator_ids', [])),
        }

        if instance.get('current_crl') is not None:
            result['current_crl'] = instance['current_crl']

        return result
