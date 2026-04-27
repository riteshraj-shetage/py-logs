from django.db import models
from django.contrib.auth.models import User
from tenants.models import Tenant


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    avatar_color = models.CharField(max_length=7, default='#007bff')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} ({self.tenant})'

    class Meta:
        ordering = ['joined_at']
