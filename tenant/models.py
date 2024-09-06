from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    
    # Email settings
    email_host = models.CharField(max_length=100, null=True, blank=True)
    email_host_user = models.CharField(max_length=100, null=True, blank=True)
    email_host_password = models.CharField(max_length=100, null=True, blank=True)
    
    # AWS settings
    aws_access_key_id = models.CharField(max_length=100, null=True, blank=True)
    aws_secret_access_key = models.CharField(max_length=100, null=True, blank=True)

    # Razorpay settings
    razorpay_key_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_key_secret = models.CharField(max_length=100, null=True, blank=True)

    # Stripe settings
    stripe_secret_key = models.CharField(max_length=100, null=True, blank=True)
    stripe_public_key = models.CharField(max_length=100, null=True, blank=True)

    # PayPal settings
    paypal_client_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_client_secret = models.CharField(max_length=255, null=True, blank=True)

    # Push Notification settings
    fcm_api_key = models.CharField(max_length=255, null=True, blank=True)
    apns_certificate = models.CharField(max_length=255, null=True, blank=True)

    # Unfold Admin customization
    unfold_site_title = models.CharField(max_length=100, default="My Charger Admin")
    unfold_site_header = models.CharField(max_length=100, default="Charger Management")
    unfold_site_icon = models.CharField(max_length=100, default="bolt")

    # Additional settings
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=10, default='INR')  # Add default currency
    country = models.CharField(max_length=100, default='India')  # Add country field
    is_active = models.BooleanField(default=True, blank=True)

    # Automatically creates schema when saving
    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass
