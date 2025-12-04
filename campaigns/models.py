from django.db import models
from django.conf import settings
from core.models import BaseModel

# Create your models here.

class Campaign(BaseModel):
    """
    Campaign model linked to a startup.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    startup = models.OneToOneField(
        'users.Startup', 
        on_delete=models.CASCADE, 
        related_name='campaign'
    )
    
    # Step 1: The Basics
    problem = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    business_model = models.TextField(blank=True, null=True)
    
    # Metadata
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    def __str__(self):
        return f"Campaign for {self.startup.company_name}"


class InvestmentRound(BaseModel):
    """
    Represents an investment round for a campaign.
    """
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'

    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='rounds'
    )
    name = models.CharField(max_length=100, help_text="e.g., 'Pre-Seed', 'Seed', 'Series A', 'Bridge'")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    pre_money_valuation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    is_current = models.BooleanField(default=False, help_text="Is this the current round for the wizard?")
    
    # Date Fields
    launch_date = models.DateField(null=True, blank=True, help_text="Date when the round officially opened")
    target_close_date = models.DateField(null=True, blank=True, help_text="Target deadline communicated to investors")
    actual_close_date = models.DateField(null=True, blank=True, help_text="Date when the round was actually closed")

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other rounds for this campaign to is_current=False
            InvestmentRound.objects.filter(
                campaign=self.campaign,
                is_current=True
            ).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Round for {self.campaign.startup.company_name}"


class Investor(BaseModel):
    """
    Represents an investor in a specific investment round.
    """
    class Status(models.TextChoices):
        CONTACTED = 'CONTACTED', 'Contacted'
        PITCH_SENT = 'PITCH_SENT', 'Pitch Sent'
        MEETING_SCHEDULED = 'MEETING_SCHEDULED', 'Meeting Scheduled'
        DUE_DILIGENCE = 'DUE_DILIGENCE', 'Due Diligence'
        TERM_SHEET = 'TERM_SHEET', 'Term Sheet'
        COMMITTED = 'COMMITTED', 'Committed'

    round = models.ForeignKey(
        InvestmentRound,
        on_delete=models.CASCADE,
        related_name='investors'
    )
    incubator = models.ForeignKey(
        'users.Incubator',
        on_delete=models.CASCADE,
        related_name='investments'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONTACTED)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        # unique_together = ('round', 'incubator')
        pass

    def __str__(self):
        return f"{self.incubator.name} in {self.round.name}"


class CampaignTeamMember(BaseModel):
    """
    Team member associated with a campaign.
    """
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='team_members'
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    linkedin = models.URLField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.role}"


class CampaignFinancials(BaseModel):
    """
    Financial information for a campaign.
    """
    campaign = models.OneToOneField(
        Campaign,
        on_delete=models.CASCADE,
        related_name='financials'
    )
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valuation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    usage_of_funds = models.JSONField(default=dict, blank=True)
    revenue_history = models.JSONField(default=dict, blank=True)

    # Current State Fields
    pre_money_valuation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pre-money valuation of the startup"
    )
    current_cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current cash balance available"
    )
    monthly_burn_rate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly burn rate (cash spent per month)"
    )

    # Financial Projections Grid
    financial_projections = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quarterly financial projections: { 'q1': { 'revenue': 0, 'cogs': 0, 'opex': 0 }, 'q2': {...}, 'q3': {...}, 'q4': {...} }"
    )

    def __str__(self):
        return f"Financials for {self.campaign.startup.company_name}"

class CampaignTraction(BaseModel):
    """
    Traction metrics and proof for a campaign.
    """
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='tractions'
    )
    metrics = models.JSONField(default=dict)
    proof_doc_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Traction for {self.campaign.startup.company_name}"


class CampaignLegal(BaseModel):
    """
    Legal documents for a campaign.
    """
    campaign = models.OneToOneField(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='legal'
    )
    constitution_url = models.URLField(blank=True, null=True)
    whitepaper_url = models.URLField(blank=True, null=True)
    cap_table_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Legal docs for {self.campaign.startup.company_name}"


class FinancialSheet(BaseModel):
    """
    Excel-like financial sheet for a campaign.
    Stores custom metrics, formulas, and values in a structured JSON format.
    """
    campaign = models.OneToOneField(
        Campaign,
        on_delete=models.CASCADE,
        related_name='financial_sheet'
    )
    sheet_data = models.JSONField(
        default=dict,
        help_text="Structure: { 'config': {...}, 'grid_rows': [...] }"
    )

    def __str__(self):
        return f"Financial Sheet for {self.campaign.startup.company_name}"
