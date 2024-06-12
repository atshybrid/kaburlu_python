from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings


USER_TYPE_CHOICES = [
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('reporter', 'Reporter'),
        ('editor', 'Editor'),
        ('user', 'User'),
    ]

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100,blank=True, null=True)
    # Specify unique related names for groups and user_permissions
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')


class Company(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    company_name = models.CharField(max_length=250,unique=True)
    onboarding_date = models.DateTimeField(default=timezone.now)
    gst_number = models.CharField(max_length=20,blank=True, null=True)
    company_type = models.CharField(max_length=100, null=True, blank=True)
    director_adhar_number = models.CharField(max_length=12, blank=True, null=True)
    director_pan_no = models.CharField(max_length=12, blank=True, null=True)
    company_pan_no = models.CharField(max_length=12,blank=True, null=True)
    address = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    subscription_amount = models.IntegerField(default=200000)
    recurring_count = models.IntegerField(default=settings.DEFAULT_COUNT)

    def __str__(self):
        return self.company_name

TEMPLATE_TYPE_CHOICES = [
        ('web_template', 'Web Template'),
        ('epaper_template', 'Epaper Template'),
        ('id_card_template', 'ID Card Template'),
        ('kaburlu_app_template', 'Kaburlu App Template'),
    ]

class Templates(models.Model):
    template_id = models.IntegerField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)








