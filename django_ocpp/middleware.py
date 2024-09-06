# django_ocpp/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_model

class TenantSettingsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.MULTITENANT:  # Only apply if MULTITENANT is True
            tenant = request.tenant
            if tenant:
                # Set tenant-specific email settings
                request.email_config = {
                    'EMAIL_HOST': tenant.email_host,
                    'EMAIL_HOST_USER': tenant.email_host_user,
                    'EMAIL_HOST_PASSWORD': tenant.email_host_password,
                }
                
                # Set tenant-specific AWS settings
                request.aws_config = {
                    'AWS_ACCESS_KEY_ID': tenant.aws_access_key_id,
                    'AWS_SECRET_ACCESS_KEY': tenant.aws_secret_access_key,
                }
                
                # Set tenant-specific Razorpay settings
                request.razorpay_config = {
                    'RAZORPAY_KEY_ID': tenant.razorpay_key_id,
                    'RAZORPAY_KEY_SECRET': tenant.razorpay_key_secret,
                }
                
                # Set tenant-specific timezone
                request.timezone = tenant.timezone
