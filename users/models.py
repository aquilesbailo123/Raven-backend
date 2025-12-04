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
    MARKETPLACE = 'Marketplace'
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

    onboarding_completed = models.BooleanField(
        default=False,
        help_text="True when user completes the onboarding wizard"
    )

    TRL_level = models.IntegerField(
        default=1,
        help_text="Current Technology Readiness Level (1-9)",
        choices=[(i, f'Level {i}') for i in range(1, 10)]
    )
    CRL_level = models.IntegerField(
        default=1,
        help_text="Current Commercial Readiness Level (1-9)",
        choices=[(i, f'Level {i}') for i in range(1, 10)]
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

    def update_maturity_levels(self):
        """
        Updates TRL_level and CRL_level based on approved ReadinessLevels.
        Logic: The current level is the highest *consecutive* level from 1 that has
        at least one APPROVED evidence.
        """
        from .models import Evidence  # Avoid circular import

        for type_code in ['TRL', 'CRL']:
            current_level = 0
            for i in range(1, 10):
                # Check if there is at least one approved evidence for this level
                has_approved_evidence = self.evidences.filter(
                    type=type_code,
                    level=i,
                    status=Evidence.APPROVED
                ).exists()

                if has_approved_evidence:
                    # If level 'i' is approved, update current_level and check the next one
                    current_level = i
                else:
                    # If level 'i' is not approved, the consecutive chain is broken
                    break
            
            # Update the corresponding field
            if type_code == 'TRL':
                self.TRL_level = current_level
            else:
                self.CRL_level = current_level
        
        self.save(update_fields=['TRL_level', 'CRL_level'])

    # Relationship to Incubators
    incubators = models.ManyToManyField(
        'Incubator',
        related_name='startups',
        blank=True,
        help_text="Incubators that this startup is associated with"
    )


class Incubator(BaseModel):
    """
    Incubator profile linked to a user.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='incubator',
        limit_choices_to={'user_type': Profile.INCUBATOR}
    )
    name = models.CharField(max_length=255, help_text="Name of the Incubator")
    profile_complete = models.BooleanField(
        default=False,
        help_text="True when incubator profile is complete"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the incubator thesis and focus"
    )
    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to incubator logo"
    )

    class Meta:
        verbose_name = 'Incubator'
        verbose_name_plural = 'Incubators'

    def __str__(self):
        return self.name


class IncubatorMember(BaseModel):
    """
    Person associated with an Incubator (Investor, Mentor, or both).
    """
    INVESTOR = 'INVESTOR'
    MENTOR = 'MENTOR'
    BOTH = 'BOTH'

    ROLE_CHOICES = [
        (INVESTOR, 'Investor'),
        (MENTOR, 'Mentor'),
        (BOTH, 'Both'),
    ]

    incubator = models.ForeignKey(
        Incubator,
        on_delete=models.CASCADE,
        related_name='members',
        help_text="Incubator this person belongs to"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=MENTOR,
        help_text="Role of the person in the incubator"
    )

    class Meta:
        verbose_name = 'Incubator Member'
        verbose_name_plural = 'Incubator Members'

    def __str__(self):
        return f"{self.full_name} ({self.role}) - {self.incubator.name}"


class Challenge(BaseModel):
    """
    Challenge launched by an Incubator.
    """
    OPEN = 'OPEN'
    CONCLUDED = 'CONCLUDED'

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (CONCLUDED, 'Concluded'),
    ]

    incubator = models.ForeignKey(
        Incubator,
        on_delete=models.CASCADE,
        related_name='challenges',
        help_text="Incubator that launched this challenge"
    )
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    required_technologies = models.TextField(help_text="Comma-separated list of technologies or description")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=OPEN
    )

    class Meta:
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return f"{self.title} - {self.incubator.name}"

    @property
    def applicant_count(self):
        return self.applications.count()


class ChallengeApplication(BaseModel):
    """
    Application/Solution from a Startup to a Challenge.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='challenge_applications'
    )
    text_solution = models.TextField(help_text="Text description of the solution")

    class Meta:
        verbose_name = 'Challenge Application'
        verbose_name_plural = 'Challenge Applications'
        unique_together = ['challenge', 'startup']

    def __str__(self):
        return f"Application by {self.startup.company_name} to {self.challenge.title}"


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
# READINESS LEVEL MODELS
# =============================================================================

class ReadinessLevel(BaseModel):
    """
    Represents a specific TRL or CRL level for a startup.
    Stores metadata (title, subtitle) and tracks the status based on evidence.
    """
    TRL = 'TRL'
    CRL = 'CRL'
    TYPE_CHOICES = [
        (TRL, 'Technology Readiness Level'),
        (CRL, 'Commercial Readiness Level'),
    ]

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='readiness_levels',
        help_text="Startup that owns this readiness level"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TRL,
        help_text="Type of readiness level (TRL or CRL)"
    )
    level = models.IntegerField(
        help_text="Level number (1-9)",
        choices=[(i, f'Level {i}') for i in range(1, 10)]
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of this level (e.g., 'Proof of Concept')"
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Subtitle or brief description"
    )

    class Meta:
        verbose_name = 'Readiness Level'
        verbose_name_plural = 'Readiness Levels'
        unique_together = ['startup', 'type', 'level']
        ordering = ['type', 'level']

    def __str__(self):
        return f"{self.startup.company_name} - {self.type} {self.level}"


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

    # Evidence type choices
    TRL = 'TRL'
    CRL = 'CRL'
    EVIDENCE_TYPE_CHOICES = [
        (TRL, 'Technology Readiness Level'),
        (CRL, 'Commercial Readiness Level'),
    ]

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='evidences',
        help_text="Startup that owns this evidence"
    )
    readiness_level = models.ForeignKey(
        'ReadinessLevel',
        on_delete=models.CASCADE,
        related_name='evidences',
        null=True,
        blank=True,
        help_text="Specific readiness level definition this evidence supports"
    )
    type = models.CharField(
        max_length=10,
        choices=EVIDENCE_TYPE_CHOICES,
        default=TRL,
        help_text="Type of readiness level (TRL or CRL)"
    )
    level = models.IntegerField(
        default=1,
        help_text="Readiness Level (1-9)",
        choices=[(i, f'Level {i}') for i in range(1, 10)]
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the evidence and what it demonstrates"
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
            models.Index(fields=['startup', 'type', 'level']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.startup.company_name} - {self.type} {self.level} - {self.status}"


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
    round = models.ForeignKey(
        'Round',
        on_delete=models.SET_NULL,
        related_name='investors',
        blank=True,
        null=True,
        help_text="Fundraising round this investor is associated with"
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


class Round(BaseModel):
    """
    Represents a fundraising round for a startup.
    These rounds might not have a specific investor tied to them initially,
    and can be used to track general fundraising progress.
    """
    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name='rounds',
        help_text="Startup that owns this fundraising round"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the fundraising round (e.g., 'Seed', 'Series A')"
    )
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Target amount to raise for this round (USD)"
    )
    raised_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Amount already raised for this round (USD)"
    )
    is_open = models.BooleanField(
        default=True,
        help_text="Indicates if the fundraising round is currently open"
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the round officially started"
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the round is expected to close or closed"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this fundraising round"
    )

    class Meta:
        verbose_name = 'Round'
        verbose_name_plural = 'Rounds'
        ordering = ['-start_date', '-created']
        # unique_together = [['startup', 'name']]
        indexes = [
            models.Index(fields=['startup', 'is_open']),
        ]

    def __str__(self):
        return f"{self.startup.company_name} - {self.name} Round"
