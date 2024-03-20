from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.gis.db import models as gis_models
import uuid


# Assuming WEB_SOCKET_PING_INTERVAL is defined somewhere in your settings
WEB_SOCKET_PING_INTERVAL = 30


# Payment Info Model
class PaymentInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payment_info')
    amount = models.FloatField()
    method = models.CharField(max_length=255)
    captured = models.BooleanField(default=False)
    refund = models.FloatField(default=0.0)
    refund_to_wallet = models.FloatField(default=0.0)
    refund_status = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True, null=True)
    international = models.BooleanField(default=False)
    fee = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    tax_description = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=50)


# Order Model
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    amount = models.FloatField()
    tax = models.FloatField()
    gateway_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_name = models.CharField(max_length=255, blank=True, null=True)
    order_serial = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=50)
    limit_type = models.CharField(max_length=50, blank=True, null=True)
    property = models.JSONField(blank=True, null=True)  # JSON stored as text
    status = models.CharField(max_length=50)


# Charging Plan Model
class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_corporate = models.BooleanField(default=False)
    corporate_domain = models.CharField(max_length=255, blank=True, null=True)
    corporate_name = models.CharField(max_length=255, blank=True, null=True)
    percent_discount_enable = models.BooleanField(default=True)
    discount_percent = models.FloatField(default=0.0)
    time_fixed_discount_enable = models.BooleanField(default=True)
    discount_fixed_time_amount = models.FloatField(default=0.0)
    kwh_fixed_discount_enable = models.BooleanField(default=True)
    discount_fixed_kwh_amount = models.FloatField(default=0.0)
    max_discount = models.FloatField(default=9999999)
    min_order_amount = models.FloatField(default=0.0)
    amount_added = models.FloatField()
    price = models.FloatField()
    free_included_time = models.FloatField()
    free_included_time_validity = models.IntegerField()
    free_included_kwh = models.FloatField()
    free_included_kwh_validity = models.IntegerField()
    plan_renewal_interval = models.IntegerField()  # in days
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=50, default='CHARGING')


# PlanUser Model
class PlanUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_users')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_users')
    expiry = models.DateTimeField()
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    validity = models.IntegerField()  # days

# Promotion Model
class Promotion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=255)
    criteria = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    value = models.FloatField()
    value_type = models.CharField(max_length=50)
    min_order_amount = models.FloatField()
    max_order_amount = models.FloatField()
    max_discount = models.FloatField()
    location = gis_models.PointField()
    radius = models.FloatField()
    max_invocation_by_an_single_user = models.IntegerField()
    eligibility = models.FloatField()
    eligibility_criteria = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    readonly = models.BooleanField(default=False)

# PushNotification Model
class PushNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=10, choices=[('ANDROID', 'Android'), ('IOS', 'iOS')], default='ANDROID')

# Role Model
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

# RolePermission Model
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module = models.CharField(max_length=255)
    permission = models.CharField(max_length=255)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module', 'permission')

# SessionBilling Model
class SessionBilling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('ChargingSession', on_delete=models.CASCADE, related_name='billings')
    amount_added = models.FloatField()
    amount_consumed = models.FloatField()
    amount_refunded = models.FloatField()
    time_added = models.FloatField()
    time_consumed = models.FloatField()
    time_refunded = models.FloatField()
    kwh_added = models.FloatField()
    kwh_consumed = models.FloatField()
    kwh_refunded = models.FloatField()

# TaxTemplate Model
class TaxTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    tax_details = models.JSONField()  # Store tax details as JSON


# Wallet Model
class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    amount = models.FloatField()
    start_balance = models.FloatField()
    end_balance = models.FloatField()
    reason = models.CharField(max_length=255, choices=[
        ('EMPLOYEE_DEPOSIT', 'Employee Deposit'),
        ('REFUND', 'Refund'),
        ('EMPLOYEE_WITHDRAW', 'Employee Withdraw'),
        ('GIFT_DEPOSIT', 'Gift Deposit'),
        ('PROMOTIONAL_DEPOSIT', 'Promotional Deposit'),
        ('HOST_DEPOSIT', 'Host Deposit'),
        ('COMPLAIN_DEPOSIT', 'Complain Deposit'),
        ('CUSTOMER_DEPOSIT', 'Customer Deposit'),
        ('CHARGE_DEDUCTION', 'Charge Deduction'),
    ])


