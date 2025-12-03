from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from .models import (
    Campaign,
    CampaignTeamMember,
    CampaignFinancials,
    CampaignTraction,
    CampaignLegal,
    InvestmentRound,
    Investor,
)


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = (
            'id',
            'name',
            'email',
            'status',
            'amount',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')


class InvestmentRoundSerializer(WritableNestedModelSerializer):
    investors = InvestorSerializer(many=True, required=False)

    class Meta:
        model = InvestmentRound
        fields = (
            'id',
            'name',
            'target_amount',
            'pre_money_valuation',
            'status',
            'is_current',
            'investors',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')


class CampaignTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTeamMember
        exclude = ('campaign',)


class CampaignFinancialsSerializer(serializers.ModelSerializer):
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
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated')


class CampaignTractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTraction
        exclude = ('campaign',)


class CampaignLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLegal
        exclude = ('campaign',)


class CampaignSerializer(WritableNestedModelSerializer):
    team_members = CampaignTeamMemberSerializer(many=True, required=False)
    financials = CampaignFinancialsSerializer(required=False)
    tractions = CampaignTractionSerializer(many=True, required=False)
    legal = CampaignLegalSerializer(required=False)
    rounds = InvestmentRoundSerializer(many=True, required=False)
    
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
        )
        read_only_fields = ('startup', 'status')