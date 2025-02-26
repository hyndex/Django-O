from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.gis.db import models as gis_models
import uuid
from push_notifications.models import APNSDevice, GCMDevice
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from random import randint

# Assuming WEB_SOCKET_PING_INTERVAL is defined somewhere in your settings
WEB_SOCKET_PING_INTERVAL = 30

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pin = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # OCPI specific fields
    ocpi_party_id = models.CharField(max_length=10, blank=True, null=True)  # Unique party ID
    ocpi_role = models.CharField(max_length=20, choices=[('CPO', 'CPO'), ('eMSP', 'eMSP')], blank=True, null=True)
    ocpi_token = models.CharField(max_length=255, blank=True, null=True)  # Store OCPI token here

    def __str__(self):
        return self.user.username



# Payment Info Model
class PaymentInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_payment_info', null=True, blank=True)
    amount = models.FloatField()
    method = models.CharField(max_length=255, default='WALLET')
    captured = models.BooleanField(default=True)
    refund = models.FloatField(default=0.0)
    refund_to_wallet = models.FloatField(default=0.0)
    refund_status = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    international = models.BooleanField(default=False)
    fee = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    tax_description = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=50, default='PAID')


# SessionBilling Model
class SessionBilling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('ocpp_app.ChargingSession', on_delete=models.CASCADE, related_name='billings')
    amount_added = models.FloatField()
    amount_consumed = models.FloatField(blank=True, null=True)
    amount_refunded = models.FloatField(blank=True, null=True)
    time_added = models.FloatField(blank=True, null=True)
    time_consumed = models.FloatField(blank=True, null=True)
    time_refunded = models.FloatField(blank=True, null=True)
    kwh_added = models.FloatField()
    kwh_consumed = models.FloatField(blank=True, null=True)
    kwh_refunded = models.FloatField(blank=True, null=True)

    # New field for OCPI CDR
    cdr_sent = models.BooleanField(default=False)


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



class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    registration_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=10, choices=[('ANDROID', 'Android'), ('IOS', 'iOS')])

    def save(self, *args, **kwargs):
        if self.device_type == 'ANDROID':
            GCMDevice.objects.update_or_create(
                registration_id=self.registration_id,
                defaults={'user': self.user, 'device_id': self.device_id}
            )
        elif self.device_type == 'IOS':
            APNSDevice.objects.update_or_create(
                registration_id=self.registration_id,
                defaults={'user': self.user, 'device_id': self.device_id}
            )
        super(Device, self).save(*args, **kwargs)



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
    amount = models.FloatField() # positive in case of deposit and negative in case of deduction
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
    ], default='CUSTOMER_DEPOSIT')



# Order Model
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    payment_info = models.OneToOneField(PaymentInfo, on_delete=models.CASCADE, related_name='order_payment_info', null=True, blank=True)
    session_billing = models.ForeignKey(SessionBilling, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    amount = models.FloatField()
    tax = models.FloatField(default=0.0)
    gateway_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_name = models.CharField(max_length=255, blank=True, null=True)
    order_serial = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=50)
    limit_type = models.CharField(max_length=50, blank=True, null=True)
    property = models.JSONField(blank=True, null=True)  # JSON stored as text
    status = models.CharField(max_length=50)



class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=[('phone', 'Phone'), ('email', 'Email')])

    def is_valid(self):
        return timezone.now() - self.created_at < timezone.timedelta(minutes=5)  # OTP is valid for 5 minutes
    
    # @classmethod
    # def create_otp(cls, user, type):
    #     code = str(randint(100000, 999999))
    #     return cls.objects.create(user=user, code=code, type=type)



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()



