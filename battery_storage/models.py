from django.db import models
from django.contrib.gis.db import models as gis_models  # For geolocation fields
from django.utils.timezone import now

# Model for Battery Storage System
class BatteryStorage(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    coordinates = gis_models.PointField(geography=True)
    capacity_mwh = models.FloatField(help_text="Storage capacity of the battery in megawatt-hours")

    def __str__(self):
        return self.name

# Model for Battery Usage Logs
class BatteryUsageLog(models.Model):
    battery_storage = models.ForeignKey(BatteryStorage, on_delete=models.CASCADE, related_name="usage_logs")
    timestamp = models.DateTimeField(default=now)
    energy_input_mwh = models.FloatField(help_text="Energy input to the battery in megawatt-hours", null=True, blank=True)
    energy_output_mwh = models.FloatField(help_text="Energy output from the battery in megawatt-hours", null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('charging', 'Charging'), ('discharging', 'Discharging')], default='charging')

    def __str__(self):
        return f"{self.battery_storage.name} - {self.status} at {self.timestamp}"
