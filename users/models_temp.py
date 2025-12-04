from django.db import models
from core.models import BaseModel
from .models import Startup

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
