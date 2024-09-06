from pathlib import Path
import os
from dotenv import load_dotenv
from django.core.cache import cache
from django.utils.timezone import activate

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Basic settings
SECRET_KEY = os.getenv('SECRET_KEY')
MULTITENANT = os.getenv('MULTITENANT', 'False') == 'True'
DEBUG = os.getenv('DEBUG') == 'True'


# Django Payments configuration
PAYMENTS_PLUGINS = ['payments.stripe', 'payments.razorpay', 'payments.paypal']

# Default Payment Variants, will be updated per tenant
PAYMENT_VARIANTS = {
    'stripe': ('payments.stripe.StripeProvider', {
        'secret_key': os.getenv('STRIPE_SECRET_KEY', ''),
        'public_key': os.getenv('STRIPE_PUBLIC_KEY', ''),
    }),
    'razorpay': ('payments.razorpay.RazorpayProvider', {
        'key_id': os.getenv('RAZORPAY_KEY_ID', ''),
        'key_secret': os.getenv('RAZORPAY_KEY_SECRET', ''),
    }),
    'paypal': ('payments.paypal.PayPalProvider', {
        'client_id': os.getenv('PAYPAL_CLIENT_ID', ''),
        'client_secret': os.getenv('PAYPAL_CLIENT_SECRET', ''),
    }),
}

# Dynamic tenant-based payment variants
def get_payment_variants(tenant):
    variants = {}
    
    if tenant.stripe_secret_key:
        variants['stripe'] = ('payments.stripe.StripeProvider', {
            'secret_key': tenant.stripe_secret_key,
            'public_key': tenant.stripe_public_key,
        })
    
    if tenant.razorpay_key_id:
        variants['razorpay'] = ('payments.razorpay.RazorpayProvider', {
            'key_id': tenant.razorpay_key_id,
            'key_secret': tenant.razorpay_key_secret,
        })
    
    if tenant.paypal_client_id:
        variants['paypal'] = ('payments.paypal.PayPalProvider', {
            'client_id': tenant.paypal_client_id,
            'client_secret': tenant.paypal_client_secret,
        })
    
    return variants


# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend' if MULTITENANT else 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

# Apply default settings if MULTITENANT is False
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
FCM_API_KEY = os.getenv('FCM_API_KEY')
APNS_CERTIFICATE = os.getenv('APNS_CERTIFICATE')
TIME_ZONE = 'Asia/Kolkata'  # Your existing timezone

# Default Unfold settings
UNFOLD = {
    "SITE_TITLE": "My Charger Admin",
    "SITE_HEADER": "Charger Management",
    "SITE_ICON": "bolt",
}

# Tenant-specific settings when MULTITENANT is enabled
if MULTITENANT:
    from django_tenants.utils import get_tenant_model
    from django.db import connection  # For multi-tenancy schema access

    def get_tenant_setting(key, default=None):
        tenant = get_tenant_model().objects.get(schema_name=connection.schema_name)
        cache_key = f"{tenant.schema_name}_{key}"
        setting = cache.get(cache_key)
        if not setting:
            setting = getattr(tenant, key, default)
            cache.set(cache_key, setting, timeout=3600)  # Cache for 1 hour
        return setting

    EMAIL_HOST = get_tenant_setting('email_host', default=os.getenv('EMAIL_HOST'))
    EMAIL_HOST_USER = get_tenant_setting('email_host_user', default=os.getenv('EMAIL_HOST_USER'))
    EMAIL_HOST_PASSWORD = get_tenant_setting('email_host_password', default=os.getenv('EMAIL_HOST_PASSWORD'))
    AWS_ACCESS_KEY_ID = get_tenant_setting('aws_access_key_id', default=os.getenv('AWS_ACCESS_KEY_ID'))
    AWS_SECRET_ACCESS_KEY = get_tenant_setting('aws_secret_access_key', default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    FCM_API_KEY = get_tenant_setting('fcm_api_key', default=os.getenv('FCM_API_KEY'))
    APNS_CERTIFICATE = get_tenant_setting('apns_certificate', default=os.getenv('APNS_CERTIFICATE'))

    # Set tenant-specific timezone
    TIME_ZONE = get_tenant_setting('timezone', default='UTC')
    activate(TIME_ZONE)

    # Tenant-specific Unfold admin settings
    UNFOLD = {
        "SITE_TITLE": get_tenant_setting('unfold_site_title', default="My Charger Admin"),
        "SITE_HEADER": get_tenant_setting('unfold_site_header', default="Charger Management"),
        "SITE_ICON": get_tenant_setting('unfold_site_icon', default="bolt"),
    }


# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

# Allowed hosts
ALLOWED_HOSTS = ['*']

# Applications
if MULTITENANT:
    SHARED_APPS = (
        'django_tenants',  # Required for Django-tenants
        'tenant',  # App where tenant models are located
        "unfold",
        "unfold.contrib.filters",  # optional, if special filters are needed
        "unfold.contrib.forms",  # optional, if special form elements are needed
        "unfold.contrib.import_export",  # optional, if django-import-export package is used
        "unfold.contrib.guardian",  # optional, if django-guardian package is used
        "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',

    )

    TENANT_APPS = (
        "unfold",
        "unfold.contrib.filters",  # optional, if special filters are needed
        "unfold.contrib.forms",  # optional, if special form elements are needed
        "unfold.contrib.import_export",  # optional, if django-import-export package is used
        "unfold.contrib.guardian",  # optional, if django-guardian package is used
        "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.sessions',
        'django.contrib.messages',
        'ocpp_app',
        'partners',
        'users',
        'ocpi',
        'djangoaddicts.pygwalker',
        'channels',
        'rest_framework',
        'django_filters',
        'django_otp',
        'push_notifications',
        'payments',

        # Other tenant-specific apps
    )

    INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

    # Specify the tenant and domain models
    TENANT_MODEL = "tenant.Client"  # The Tenant model path
    TENANT_DOMAIN_MODEL = "tenant.Domain"  # The Domain model path

    # Database routers for Django-tenants
    DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

else:
    # Standard installed apps when multi-tenancy is disabled
    INSTALLED_APPS = [
        "unfold",
        "unfold.contrib.filters",  # optional, if special filters are needed
        "unfold.contrib.forms",  # optional, if special form elements are needed
        "unfold.contrib.import_export",  # optional, if django-import-export package is used
        "unfold.contrib.guardian",  # optional, if django-guardian package is used
        "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'ocpp_app',
        'partners',
        'users',
        'ocpi',
        'channels',
        'rest_framework',
        'django_filters',
        'django_otp',
        'push_notifications',
        'djangoaddicts.pygwalker',
    ]

# Middleware
MIDDLEWARE = []

# Add TenantMainMiddleware if MULTITENANT is enabled
if MULTITENANT:
    MIDDLEWARE.append('django_tenants.middleware.main.TenantMainMiddleware')
    MIDDLEWARE.append('django_ocpp.middleware.TenantSettingsMiddleware')

# Add the remaining middleware
MIDDLEWARE.extend([
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

# URL settings
ROOT_URLCONF = 'django_ocpp.urls'

# Django Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/minute',
        'user': '10000/minute'
    },
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for django-tenants
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI and ASGI settings
WSGI_APPLICATION = 'django_ocpp.wsgi.application'
ASGI_APPLICATION = 'django_ocpp.asgi.application'

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Channels layers configuration for Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Internationalization and timezone
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Celery configuration
CELERY_BROKER_URL = f'{REDIS_URL}/1'
CELERY_BEAT_SCHEDULE = {
    'check_for_meter_value_timeout_every_5_minutes': {
        'task': 'ocpp_app.tasks.task_check_for_meter_value_timeout',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# AWS S3 settings (ensure these are set in .env)
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Push notifications (ensure these are set in .env)
FCM_API_KEY = os.getenv('FCM_API_KEY')
APNS_CERTIFICATE = os.getenv('APNS_CERTIFICATE')
PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": FCM_API_KEY,
    "APNS_CERTIFICATE": APNS_CERTIFICATE,
}

# APPEND_SLASH = False for REST API usage
