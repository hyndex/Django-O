from django.db import models
from django.contrib.gis.db import models as gis_models  # For geolocation fields
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

# Model for Power Plant
class PowerPlant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]

    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    coordinates = gis_models.PointField(geography=True, help_text="Latitude and Longitude of the plant")
    capacity_mw = models.FloatField(help_text="Capacity of the power plant in megawatts")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track changes over time
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Power Plant"
        verbose_name_plural = "Power Plants"
        indexes = [
            models.Index(fields=['coordinates']),
        ]

    def __str__(self):
        return self.name

# Model for Energy Generation Logs
class EnergyGenerationLog(models.Model):
    power_plant = models.ForeignKey(PowerPlant, on_delete=models.CASCADE, related_name="generation_logs")
    timestamp = models.DateTimeField(default=now, db_index=True)
    energy_generated_mwh = models.DecimalField(max_digits=10, decimal_places=3, help_text="Energy generated in megawatt-hours")
    grid_exported_mwh = models.DecimalField(max_digits=10, decimal_places=3, default=0, help_text="Energy exported to grid in megawatt-hours")
    grid_loss_mwh = models.DecimalField(max_digits=10, decimal_places=3, default=0, help_text="Energy loss during transmission in megawatt-hours")

    class Meta:
        verbose_name = "Energy Generation Log"
        verbose_name_plural = "Energy Generation Logs"
        indexes = [
            models.Index(fields=['power_plant', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.power_plant.name} - {self.energy_generated_mwh} MWh at {self.timestamp}"
