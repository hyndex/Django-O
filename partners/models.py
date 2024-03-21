from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid



# Partner Commission Member Group Model
class PartnerCommissionMemberGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host_type = models.CharField(max_length=255, default='SUB-CSMS')
    enable_user_wise_bank_settlement = models.BooleanField(default=False)

# Partner Commission Member Model
class PartnerCommissionMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commission = models.FloatField(default=0)
    commission_type = models.CharField(max_length=255, default='PERCENT')
    max_amount = models.FloatField()
    min_amount = models.FloatField()
    min_threshold = models.FloatField()
    status = models.CharField(max_length=255, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    partner_commission_member_group = models.ForeignKey(PartnerCommissionMemberGroup, on_delete=models.CASCADE, related_name='commission_members')
    role = models.CharField(max_length=255, default='Admin')
    expiry = models.DateTimeField()


class ChargerCommission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commission = models.FloatField(default=0)
    commission_type = models.CharField(max_length=255, default='PERCENT')
    max_amount = models.FloatField()
    min_amount = models.FloatField()
    min_threshold = models.FloatField()
    status = models.CharField(max_length=255, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    charger_commission_group = models.ForeignKey(PartnerCommissionMemberGroup, on_delete=models.CASCADE, related_name='partners_charger_commissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default='Admin')
    expiry = models.DateTimeField()


# Bank Account Model
class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner_commission_member = models.ForeignKey(PartnerCommissionMember, on_delete=models.CASCADE, related_name='bank_accounts')
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

# Host Custom User List Model
class PartnerEmployeeList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    list_type = models.CharField(max_length=255, default='Default Driver List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    partner_commission_member_group = models.ForeignKey(PartnerCommissionMemberGroup, on_delete=models.CASCADE, related_name='custom_user_lists')

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



# Commission Payment Model
class CommissionPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField()
    status = models.CharField(max_length=255, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_billing = models.ForeignKey('users.SessionBilling', on_delete=models.CASCADE, related_name='commission_payments')
    charger_commission_member = models.ForeignKey(PartnerCommissionMember, on_delete=models.CASCADE, related_name='commission_payments')

