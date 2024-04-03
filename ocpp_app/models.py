from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.utils.timezone import now
from partners.models import PartnerCommissionMemberGroup
from django.conf import settings
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import PlanUser, SessionBilling, Order, Wallet, PaymentInfo
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db.models import Sum
from django.db import transaction
from dateutil import parser

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
            return time_difference.total_seconds() <= (int(settings.WEB_SOCKET_PING_INTERVAL) + 10)
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
    transaction_id = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    meter_start = models.FloatField()
    meter_stop = models.FloatField(null=True, blank=True)
    reservation_id = models.CharField(max_length=255, null=True, blank=True)
    limit = models.FloatField(null=True, blank=True)
    reason = models.CharField(max_length=50, choices=[('DeAuthorized', 'DeAuthorized'), ('EmergencyStop', 'EmergencyStop'), ('EVDisconnected', 'EVDisconnected'), ('HardReset', 'HardReset'), ('Local', 'Local'), ('Other', 'Other'), ('PowerLoss', 'PowerLoss'), ('Reboot', 'Reboot'), ('Remote', 'Remote'), ('SoftReset', 'SoftReset'), ('UnlockCommand', 'UnlockCommand'), ('Server', 'Server'), ('Timeout', 'Timeout')])
    limit_type = models.CharField(max_length=10, default='KWH', choices=[('KWH', 'KWH'), ('TIME', 'TIME'), ('SOC', 'SOC'), ('FULL', 'FULL')])
    id_tag = models.ForeignKey('IdTag', on_delete=models.CASCADE, related_name='start_sessions')
    stop_id_tag = models.ForeignKey('IdTag', on_delete=models.SET_NULL, blank=True, null=True, related_name='stop_sessions')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            last_session = ChargingSession.objects.order_by('-transaction_id').first()
            self.transaction_id = (last_session.transaction_id + 1) if last_session else 1
        super().save(*args, **kwargs)

    @property
    def formatted_transaction_id(self):
        return str(self.transaction_id).zfill(9)
    
    def calculate_cost(self):
        consumed_kwh = (self.meter_stop - self.meter_start)/1000
        cost = consumed_kwh * self.connector.charger.price_per_kwh
        return cost


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


@receiver(post_save, sender=ChargingSession)
def handle_session_completion(sender, instance, **kwargs):
    if instance.meter_stop and not kwargs.get('created', False):
        with transaction.atomic():
            if(instance.meter_stop<instance.meter_start):
                instance.meter_stop = instance.meter_start
            cost = calculate_pricing(instance, (instance.meter_stop - instance.meter_start) / 1000)
            update_financial_records(instance, cost)


def calculate_pricing(session, consumed_kwh):
    return consumed_kwh * session.connector.charger.price_per_kwh

def update_financial_records(session, cost):
    user = session.id_tag.user

    # Calculate session duration and energy consumed
    session_duration = (timezone.now() - session.start_time).total_seconds() / 3600.0  # Duration in hours
    consumed_kwh = (session.meter_stop - session.meter_start) / 1000

    # Update SessionBilling
    session_billing, created = SessionBilling.objects.get_or_create(session=session)
    if created:
        session_billing.amount_consumed = cost
        session_billing.kwh_consumed = consumed_kwh
        session_billing.time_consumed = session_duration
        session_billing.save()
    else:
        session_billing.amount_consumed = cost
        session_billing.kwh_consumed = consumed_kwh
        session_billing.time_consumed = session_duration
        session_billing.save(update_fields=['amount_consumed', 'kwh_consumed', 'time_consumed'])

    # Handle Order and PaymentInfo
    order = Order.objects.get(session_billing=session_billing)
    potential_billing_amount = min(order.amount, cost)
    payment_info, payment_info_created = PaymentInfo.objects.get_or_create(order=order, amount=potential_billing_amount)
    order.payment_info = payment_info
    order.save()

    # Handle Wallet balance and transactions
    current_balance = Wallet.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0.0
    # if current_balance >= potential_billing_amount:
    #     # Deduct the cost from the wallet by adding a new Wallet entry with a negative amount
    #     new_wallet_entry = Wallet.objects.create(
    #         user=user,
    #         amount=-potential_billing_amount,
    #         start_balance=current_balance,
    #         end_balance=current_balance - potential_billing_amount,
    #         reason="CHARGE_DEDUCTION"
    #     )
    # else:
    #     # Handle insufficient funds scenario
    #     # Depending on your application, you may want to send a notification to the user, log an error, etc.
    #     pass

    new_wallet_entry = Wallet.objects.create(
        user=user,
        amount=-potential_billing_amount,
        start_balance=current_balance,
        end_balance=current_balance - potential_billing_amount,
        reason="CHARGE_DEDUCTION"
    )

    # Update the Order to reflect the payment
    order.status = 'Paid'
    order.wallet = new_wallet_entry  # Link the wallet transaction to the order
    order.save()

