from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid


# Assuming WEB_SOCKET_PING_INTERVAL is defined somewhere in your settings
WEB_SOCKET_PING_INTERVAL = 30


# Charger Owner Model
class ChargerOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    contact_info = models.EmailField()


# Bank Account Model
class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(ChargerOwner, on_delete=models.CASCADE, related_name='bank_accounts')
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    micr_code = models.CharField(max_length=9)
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)


# Settlement Model
class Settlement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField()
    reason = models.CharField(max_length=255)
    note = models.TextField()

# SettlementRequest Model
class SettlementRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField()
    status = models.CharField(max_length=255)
    note = models.TextField()

# Partner Commission Group Model
class PartnerCommissionGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host_type = models.CharField(max_length=255, default='SUB-CSMS')
    enable_user_wise_bank_settlement = models.BooleanField(default=False)

# Partner Commission Model
class PartnerCommission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commission = models.FloatField(default=0)
    commission_type = models.CharField(max_length=255, default='PERCENT')
    max_amount = models.FloatField()
    min_amount = models.FloatField()
    min_threshold = models.FloatField()
    status = models.CharField(max_length=255, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    partner_commission_group = models.ForeignKey(PartnerCommissionGroup, on_delete=models.CASCADE, related_name='commissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default='Admin')
    expiry = models.DateTimeField()

# Partner Commission Group User Model
class PartnerCommissionGroupUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=255, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    partner_commission_group = models.ForeignKey(PartnerCommissionGroup, on_delete=models.CASCADE, related_name='users')

# Host Custom User List Model
class PartnerEmployeeList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    list_type = models.CharField(max_length=255, default='Default Driver List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    partner_commission_group = models.ForeignKey(PartnerCommissionGroup, on_delete=models.CASCADE, related_name='custom_user_lists')

# User Host Custom User List Model
class UserPartnerEmployeeList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    host_custom_user_list = models.ForeignKey(PartnerEmployeeList, on_delete=models.CASCADE, related_name='user_lists')
    address = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pin = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
