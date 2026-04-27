from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tenants')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=5)
    max_projects = models.IntegerField(default=3)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
