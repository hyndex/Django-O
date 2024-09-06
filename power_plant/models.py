from django.db import models
from django.contrib.gis.db import models as gis_models  # For geolocation fields
from django.utils.timezone import now

# Model for Power Plant
class PowerPlant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    coordinates = gis_models.PointField(geography=True)  # Storing latitude and longitude
    capacity_mw = models.FloatField(help_text="Capacity of the power plant in megawatts")

    def __str__(self):
        return self.name

# Model for Energy Generation Logs
class EnergyGenerationLog(models.Model):
    power_plant = models.ForeignKey(PowerPlant, on_delete=models.CASCADE, related_name="generation_logs")
    timestamp = models.DateTimeField(default=now)
    energy_generated_mwh = models.FloatField(help_text="Energy generated in megawatt-hours")

    def __str__(self):
        return f"{self.power_plant.name} - {self.energy_generated_mwh} MWh at {self.timestamp}"

