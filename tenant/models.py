from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    email_host = models.CharField(max_length=100, null=True, blank=True)
    email_host_user = models.CharField(max_length=100, null=True, blank=True)
    email_host_password = models.CharField(max_length=100, null=True, blank=True)
    aws_access_key_id = models.CharField(max_length=100, null=True, blank=True)
    aws_secret_access_key = models.CharField(max_length=100, null=True, blank=True)
    razorpay_key_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_key_secret = models.CharField(max_length=100, null=True, blank=True)
    fcm_api_key = models.CharField(max_length=255, null=True, blank=True)  # Firebase Cloud Messaging key
    apns_certificate = models.CharField(max_length=255, null=True, blank=True)  # Apple Push Notification cert
    unfold_site_title = models.CharField(max_length=100, default="My Charger Admin")  # Unfold customization
    unfold_site_header = models.CharField(max_length=100, default="Charger Management")
    unfold_site_icon = models.CharField(max_length=100, default="bolt")  # Unfold Material icon
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True, blank=True)
    
    # Automatically creates schema when saving
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass
