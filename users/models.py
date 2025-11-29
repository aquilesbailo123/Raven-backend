from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.models import BaseModel, UserMixinModel

User = get_user_model()

class Profile(BaseModel):
    """User profile with additional information and security settings"""

    # User type choices
    STARTUP = 'startup'
    INCUBATOR = 'incubator'

    USER_TYPE_CHOICES = [
        (STARTUP, 'Startup'),
        (INCUBATOR, 'Incubator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=STARTUP,
        help_text="Type of user account"
    )

    # Security settings
    actions_freezed_till = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"
    
    def set_actions_freeze(self, hours=24):
        """Freeze user actions for specified hours"""
        self.actions_freezed_till = timezone.now() + timedelta(hours=hours)
        self.save()
    
    def is_actions_frozen(self):
        """Check if user actions are currently frozen"""
        if not self.actions_freezed_till:
            return False
        return timezone.now() < self.actions_freezed_till

class Startup(BaseModel):
    """Startup company information linked to a user profile"""

    # Industry choices
    TECHNOLOGY = 'technology'
    FINTECH = 'fintech'
    HEALTHTECH = 'healthtech'
    EDTECH = 'edtech'
    ECOMMERCE = 'ecommerce'
    SAAS = 'saas'
    AI_ML = 'ai_ml'
    BLOCKCHAIN = 'blockchain'
    MARKETPLACE = 'marketplace'
    OTHER = 'other'

    INDUSTRY_CHOICES = [
        (TECHNOLOGY, 'Technology'),
        (FINTECH, 'FinTech'),
        (HEALTHTECH, 'HealthTech'),
        (EDTECH, 'EdTech'),
        (ECOMMERCE, 'E-commerce'),
        (SAAS, 'SaaS'),
        (AI_ML, 'AI/ML'),
        (BLOCKCHAIN, 'Blockchain'),
        (MARKETPLACE, 'Marketplace'),
        (OTHER, 'Other'),
    ]

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='startup',
        limit_choices_to={'user_type': Profile.STARTUP}
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(
        max_length=50,
        choices=INDUSTRY_CHOICES,
        blank=True,
        null=True
    )
    logo_url = models.URLField(blank=True, null=True, help_text="URL to company logo in GCS")
    is_mock_data = models.BooleanField(default=True, help_text="Indicates if this is mock/sample data")
    onboarding_completed = models.BooleanField(
        default=False,
        help_text="True when user completes the onboarding wizard"
    )

    class Meta:
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'

    def __str__(self):
        return f"{self.company_name or 'Unnamed Startup'} - {self.profile.user.email}"

    def is_onboarding_complete(self):
        """
        Check if the startup has completed the onboarding wizard.
        This is now a simple field check instead of complex validation.
        """
        return self.onboarding_completed


class LoginHistory(UserMixinModel):
    """Tracks user login attempts with IP and user agent information"""
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Login history'
        verbose_name_plural = 'Login histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.ip} - {self.timestamp}"


# =============================================================================
# ONBOARDING WIZARD MODELS - Phase 2
# =============================================================================

class Evidence(BaseModel):
    """
    Evidence documentation for TRL/CRL maturity levels.
    Stores files and descriptions for technology and commercial readiness validation.
    """

    # Status choices for evidence approval workflow
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='evidences',
        help_text="Startup that owns this evidence"
    )
    trl_level = models.IntegerField(
        help_text="Technology Readiness Level (1-9)",
        choices=[(i, f'TRL {i}') for i in range(1, 10)]
    )
    description = models.TextField(
        help_text="Description of the evidence and what it demonstrates"
    )
    file = models.FileField(
        upload_to='evidence/%Y/%m/',
        help_text="Evidence file (PDF, image, video, etc.)",
        blank=True,
        null=True
    )
    file_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to evidence file in cloud storage (e.g., GCS)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Approval status of this evidence"
    )
    reviewer_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes from reviewer about this evidence"
    )

    class Meta:
        verbose_name = 'Evidence'
        verbose_name_plural = 'Evidences'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['startup', 'trl_level']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.startup.company_name} - TRL {self.trl_level} - {self.status}"


class FinancialInput(BaseModel):
    """
    Financial data inputs for startup financial projections.
    Stores monthly/periodic financial metrics for cash flow analysis.
    """

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='financial_inputs',
        help_text="Startup that owns this financial data"
    )
    period_date = models.DateField(
        help_text="Date representing the period (usually month-end)"
    )
    revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Total revenue for the period"
    )
    costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Total costs/expenses for the period"
    )
    cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Cash balance at the end of the period"
    )
    monthly_burn = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Monthly burn rate (cash spent per month)"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this period's finances"
    )

    class Meta:
        verbose_name = 'Financial Input'
        verbose_name_plural = 'Financial Inputs'
        ordering = ['-period_date']
        unique_together = [['startup', 'period_date']]
        indexes = [
            models.Index(fields=['startup', 'period_date']),
        ]

    def __str__(self):
        return f"{self.startup.company_name} - {self.period_date.strftime('%Y-%m')}"

    @property
    def net_cash_flow(self):
        """Calculate net cash flow for the period"""
        return self.revenue - self.costs


class InvestorPipeline(BaseModel):
    """
    Investor pipeline tracking for fundraising rounds.
    Manages relationships with potential and committed investors.
    """

    # Stage choices for investor relationship status
    CONTACTED = 'CONTACTED'
    PITCH_SENT = 'PITCH_SENT'
    MEETING_SCHEDULED = 'MEETING_SCHEDULED'
    DUE_DILIGENCE = 'DUE_DILIGENCE'
    TERM_SHEET = 'TERM_SHEET'
    COMMITTED = 'COMMITTED'
    DECLINED = 'DECLINED'

    STAGE_CHOICES = [
        (CONTACTED, 'Initial Contact'),
        (PITCH_SENT, 'Pitch Deck Sent'),
        (MEETING_SCHEDULED, 'Meeting Scheduled'),
        (DUE_DILIGENCE, 'Due Diligence'),
        (TERM_SHEET, 'Term Sheet Negotiation'),
        (COMMITTED, 'Committed'),
        (DECLINED, 'Declined'),
    ]

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='investor_pipeline',
        help_text="Startup that owns this investor relationship"
    )
    investor_name = models.CharField(
        max_length=255,
        help_text="Name of the investor or investment firm"
    )
    investor_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email for the investor"
    )
    stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default=CONTACTED,
        help_text="Current stage of the investor relationship"
    )
    ticket_size = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Expected or committed investment amount (USD)",
        blank=True,
        null=True
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about this investor relationship"
    )
    next_action_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date for next scheduled action/follow-up"
    )

    class Meta:
        verbose_name = 'Investor Pipeline Entry'
        verbose_name_plural = 'Investor Pipeline'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['startup', 'stage']),
        ]

    def __str__(self):
        return f"{self.startup.company_name} - {self.investor_name} ({self.stage})"