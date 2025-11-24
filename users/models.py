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