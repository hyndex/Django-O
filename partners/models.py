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


# UserHostCustomUserList Model
class UserHostCustomUserList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_user_lists')
    is_blocked = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pin = models.CharField(max_length=10, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # Additional field to determine if the list entry has expired
    is_expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.expiry_date and now() > self.expiry_date:
            self.is_expired = True
        super(UserHostCustomUserList, self).save(*args, **kwargs)

# UserHostCustomUserListMovement Model
class UserHostCustomUserListMovement(models.Model):
    user_list_entry = models.ForeignKey(UserHostCustomUserList, on_delete=models.CASCADE, related_name='movements')
    coordinates = gis_models.PointField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    @property
    def online(self):
        time_difference = now() - self.timestamp
        return time_difference.total_seconds() <= (WEB_SOCKET_PING_INTERVAL + 10)
