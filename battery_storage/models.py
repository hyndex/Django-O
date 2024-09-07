from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

# Model for Battery Storage System
class BatteryStorage(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('offline', 'Offline'),
    ]

    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    coordinates = gis_models.PointField(geography=True, help_text="Latitude and Longitude of the battery storage")
    capacity_mwh = models.DecimalField(max_digits=10, decimal_places=3, help_text="Total storage capacity in megawatt-hours")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    charge_efficiency = models.DecimalField(max_digits=5, decimal_places=2, help_text="Charge efficiency as a percentage (0-100)", default=95.0)
    discharge_efficiency = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discharge efficiency as a percentage (0-100)", default=95.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Track changes over time
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Battery Storage"
        verbose_name_plural = "Battery Storages"
        indexes = [
            models.Index(fields=['coordinates']),
        ]

    def __str__(self):
        return self.name

# Model for Battery Usage Logs
class BatteryUsageLog(models.Model):
    USAGE_CHOICES = [
        ('charging', 'Charging'),
        ('discharging', 'Discharging'),
        ('idle', 'Idle'),
    ]

    battery_storage = models.ForeignKey(BatteryStorage, on_delete=models.CASCADE, related_name="usage_logs")
    timestamp = models.DateTimeField(default=now, db_index=True)
    energy_input_mwh = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Energy input to the battery in MWh")
    energy_output_mwh = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Energy output from the battery in MWh")
    efficiency_loss_mwh = models.DecimalField(max_digits=10, decimal_places=3, default=0, help_text="Loss due to efficiency")
    state_of_charge = models.DecimalField(max_digits=5, decimal_places=2, help_text="Current state of charge as percentage (0-100)", default=0.0)
    usage_status = models.CharField(max_length=50, choices=USAGE_CHOICES, default='idle')
    
    class Meta:
        verbose_name = "Battery Usage Log"
        verbose_name_plural = "Battery Usage Logs"
        indexes = [
            models.Index(fields=['battery_storage', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.battery_storage.name} - {self.usage_status} at {self.timestamp}"
