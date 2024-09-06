# django_ocpp/middleware.py

from django.utils.deprecation import MiddlewareMixin

class TenantSettingsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'tenant'):  # Ensure request has tenant info
            tenant = request.tenant
            
            # Set tenant-specific email, AWS, Razorpay, Stripe, and timezone settings
            request.email_config = {
                'EMAIL_HOST': tenant.email_host,
                'EMAIL_HOST_USER': tenant.email_host_user,
                'EMAIL_HOST_PASSWORD': tenant.email_host_password,
            }
            
            request.aws_config = {
                'AWS_ACCESS_KEY_ID': tenant.aws_access_key_id,
                'AWS_SECRET_ACCESS_KEY': tenant.aws_secret_access_key,
            }
            
            request.razorpay_config = {
                'RAZORPAY_KEY_ID': tenant.razorpay_key_id,
                'RAZORPAY_KEY_SECRET': tenant.razorpay_key_secret,
            }

            request.stripe_config = {
                'STRIPE_SECRET_KEY': tenant.stripe_secret_key,
                'STRIPE_PUBLIC_KEY': tenant.stripe_public_key,
            }
            
            request.timezone = tenant.timezone
