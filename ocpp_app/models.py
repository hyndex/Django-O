from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.utils.timezone import now
from partners.models import PartnerCommissionMemberGroup
from django.conf import settings
from django.db.models import Max

class Charger(models.Model):
    id = models.AutoField(primary_key=True)
    charger_id = models.CharField(max_length=50, unique=True)  # Represents the OCPP charger ID
    meter_value_interval = models.IntegerField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    last_csms = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    enabled = models.BooleanField(default=False)
    price_per_kwh = models.FloatField(default=20)
    verified = models.BooleanField(default=False)
    charger_commission_group = models.ForeignKey(PartnerCommissionMemberGroup, on_delete=models.DO_NOTHING, blank=True, null=True,related_name='ocpp_charger_commissions')
    type = models.CharField(max_length=10, default='AC', choices=[('AC', 'AC'), ('DC', 'DC'), ('BOTH', 'BOTH')])
    coordinates = gis_models.PointField(geography=True, blank=True, null=True)
    
    @property
    def online(self):
        if self.last_heartbeat:
            time_difference = now() - self.last_heartbeat
            return time_difference.total_seconds() <= (settings.WEB_SOCKET_PING_INTERVAL + 10)  # Adjust the interval as needed
        return False
    
    def __str__(self):
        return f"{self.charger_id} - {self.vendor} {self.model}"


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

    def save(self, *args, **kwargs):
        if not self.connector_id:
            max_connector_id = self.charger.connectors.aggregate(Max('connector_id'))['connector_id__max']
            self.connector_id = (max_connector_id or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Connector {self.connector_id} for {self.charger}"
    
    
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

class MeterValues(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=255)
    unit = models.CharField(max_length=255, null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)
    context = models.CharField(max_length=255, null=True, blank=True)
    measurand = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField()
    charging_session = models.ForeignKey(
        ChargingSession,
        on_delete=models.CASCADE,
        related_name='meter_values',
        null=True,
        blank=True
    )
    connector = models.ForeignKey(
        Connector,
        on_delete=models.CASCADE,
        related_name='meter_values',
        null=True,
        blank=True
    )
    charger = models.ForeignKey(
        Charger,
        on_delete=models.CASCADE,
        related_name='meter_values',
        null=True,
        blank=True
    )




