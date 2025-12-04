from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from users.models import Incubator

from .models import (
    Campaign,
    CampaignTeamMember,
    CampaignFinancials,
    CampaignTraction,
    CampaignLegal,
    InvestmentRound,
    Investor,
    FinancialSheet,
)


class InvestorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    incubator_id = serializers.PrimaryKeyRelatedField(
        queryset=Incubator.objects.all(),
        source='incubator',
        write_only=True
    )
    incubator_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Investor
        fields = (
            'id',
            'incubator_id',
            'incubator_details',
            'status',
            'amount',
            'created',
            'updated',
        )
        read_only_fields = ('created', 'updated', 'incubator_details')

    def get_incubator_details(self, obj):
        return {
            "id": obj.incubator.id,
            "name": obj.incubator.name
        }


class InvestmentRoundSerializer(WritableNestedModelSerializer):
    investors = InvestorSerializer(many=True, required=False)
    total_committed_amount = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentRound
        fields = (
            'id',
            'name',
            'target_amount',
            'pre_money_valuation',
            'status',
            'is_current',
            'launch_date',
            'target_close_date',
            'actual_close_date',
            'investors',
            'total_committed_amount',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')

    def get_total_committed_amount(self, obj):
        return sum(inv.amount for inv in obj.investors.all() if inv.status == Investor.Status.COMMITTED)

    def update(self, instance, validated_data):
        investors_data = validated_data.pop('investors', None)
        
        # Update the InvestmentRound instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if investors_data is not None:
            # 1. Identify existing investors
            existing_investors = {inv.id: inv for inv in instance.investors.all()}
            existing_ids = set(existing_investors.keys())
            
            # 2. Identify incoming IDs
            incoming_ids = set()
            for inv_data in investors_data:
                if 'id' in inv_data and inv_data['id']:
                    incoming_ids.add(inv_data['id'])
            
            # 3. Delete investors not in incoming data
            to_delete_ids = existing_ids - incoming_ids
            if to_delete_ids:
                Investor.objects.filter(id__in=to_delete_ids).delete()
            
            # 4. Create or Update investors
            for inv_data in investors_data:
                inv_id = inv_data.get('id')
                if inv_id and inv_id in existing_investors:
                    # Update existing
                    investor = existing_investors[inv_id]
                    for attr, value in inv_data.items():
                        if attr != 'id': # Don't update ID
                            setattr(investor, attr, value)
                    investor.save()
                else:
                    # Create new
                    # Remove 'id' if present but None or not in existing (though if not in existing it shouldn't have ID usually)
                    inv_data.pop('id', None) 
                    Investor.objects.create(round=instance, **inv_data)

        return instance


class CampaignTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTeamMember
        exclude = ('campaign',)


class CampaignFinancialsSerializer(serializers.ModelSerializer):
    total_capital_injection = serializers.SerializerMethodField()
    class Meta:
        model = CampaignFinancials
        fields = (
            'id',
            'funding_goal',
            'valuation',
            'usage_of_funds',
            'revenue_history',
            'pre_money_valuation',
            'current_cash_balance',
            'monthly_burn_rate',
            'financial_projections',
            'total_capital_injection',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')

    def get_total_capital_injection(self, obj):
        # Sum committed amount from all rounds associated with the campaign
        total = 0
        if hasattr(obj, 'campaign'):
             for round in obj.campaign.rounds.all():
                  total += sum(inv.amount for inv in round.investors.all() if inv.status == Investor.Status.COMMITTED)
        return total


class CampaignTractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTraction
        exclude = ('campaign',)


class CampaignLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLegal
        exclude = ('campaign',)


class FinancialSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialSheet
        fields = (
            'id',
            'sheet_data',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')


class CampaignSerializer(WritableNestedModelSerializer):
    team_members = CampaignTeamMemberSerializer(many=True, required=False)
    financials = CampaignFinancialsSerializer(required=False)
    tractions = CampaignTractionSerializer(many=True, required=False)
    legal = CampaignLegalSerializer(required=False)
    rounds = InvestmentRoundSerializer(many=True, required=False)
    financial_sheet = FinancialSheetSerializer(required=False)
    
    class Meta:
        model = Campaign
        fields = (
            'id',
            'startup',
            'problem',
            'solution',
            'business_model',
            'status',
            'team_members',
            'financials',
            'tractions',
            'legal',
            'rounds',
            'financial_sheet',
        )
        read_only_fields = ('startup', 'status')