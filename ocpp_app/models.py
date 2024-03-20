from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Charger(models.Model):
    id = models.AutoField(primary_key=True)
    charger_id = models.CharField(max_length=50, unique=True)  # Represents the OCPP charger ID
    meter_value_interval = models.IntegerField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    last_csms = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    enabled = models.BooleanField(default=False)
    price_per_kwh = models.FloatField(default=20)
    verified = models.BooleanField(default=False)
    type = models.CharField(max_length=10, default='AC', choices=[('AC', 'AC'), ('DC', 'DC'), ('BOTH', 'BOTH')])

    @property
    def online(self):
        if self.last_heartbeat:
            time_difference = now() - self.last_heartbeat
            return time_difference.total_seconds() <= (WEB_SOCKET_PING_INTERVAL + 10)  # Adjust the interval as needed
        return False

class ChargerConfig(models.Model):
    id = models.AutoField(primary_key=True)
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name='configs')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    readonly = models.BooleanField(default=False)

class Connector(models.Model):
    id = models.AutoField(primary_key=True)
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name='connectors')
    connector_id = models.IntegerField()
    status = models.CharField(max_length=20, default='Unavailable', choices=[('Available', 'Available'), ('Preparing', 'Preparing'), ('Charging', 'Charging'), ('SuspendedEVSE', 'SuspendedEVSE'), ('SuspendedEV', 'SuspendedEV'), ('Finishing', 'Finishing'), ('Reserved', 'Reserved'), ('Unavailable', 'Unavailable'), ('Faulted', 'Faulted')])
    type = models.CharField(max_length=20, default='CCS1', choices=[('IEC60309', 'IEC60309'), ('CCS2', 'CCS2'), ('CCS1', 'CCS1'), ('CHADEMO', 'CHADEMO'), ('TYPE1', 'TYPE1'), ('TYPE2', 'TYPE2'), ('IEC62196', 'IEC62196'), ('3PIN', '3PIN')])

class ChargingSession(models.Model):
    id = models.AutoField(primary_key=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='sessions')
    transaction_id = models.IntegerField(unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    meter_start = models.FloatField()
    meter_stop = models.FloatField(null=True, blank=True)
    reservation_id = models.CharField(max_length=255, null=True, blank=True)
    limit = models.FloatField(null=True, blank=True)
    reason = models.CharField(max_length=50, choices=[('DeAuthorized', 'DeAuthorized'), ('EmergencyStop', 'EmergencyStop'), ('EVDisconnected', 'EVDisconnected'), ('HardReset', 'HardReset'), ('Local', 'Local'), ('Other', 'Other'), ('PowerLoss', 'PowerLoss'), ('Reboot', 'Reboot'), ('Remote', 'Remote'), ('SoftReset', 'SoftReset'), ('UnlockCommand', 'UnlockCommand'), ('Server', 'Server'), ('Timeout', 'Timeout')])
    limit_type = models.CharField(max_length=10, default='KWH', choices=[('KWH', 'KWH'), ('TIME', 'TIME'), ('SOC', 'SOC'), ('FULL', 'FULL')])
    id_tag = models.ForeignKey('IdTag', on_delete=models.CASCADE, related_name='start_sessions')
    stop_id_tag = models.ForeignKey('IdTag', on_delete=models.SET_NULL, null=True, related_name='stop_sessions')

    @property
    def formatted_transaction_id(self):
        return str(self.transaction_id).zfill(9)

class IdTag(models.Model):
    id = models.AutoField(primary_key=True)
    idtag = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='id_tags')
    parent_idtag = models.CharField(max_length=50, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        return self.expiry_date and now() > self.expiry_date

