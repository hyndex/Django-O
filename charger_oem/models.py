from django.db import models
from django.utils import timezone

class ChargerModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Firmware(models.Model):
    model = models.ForeignKey(ChargerModel, on_delete=models.CASCADE)
    version = models.CharField(max_length=100)
    file = models.FileField(upload_to='firmware/')

    def __str__(self):
        return f'{self.model.name} - {self.version}'

class Charger(models.Model):
    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(max_length=100, unique=True)
    public_key = models.TextField()
    model = models.ForeignKey(ChargerModel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.unique_id

class IPLog(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100)
    firmware_version = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.charger.id} - {self.ip_address} - {self.timestamp}"

    def save(self, *args, **kwargs):
        super(IPLog, self).save(*args, **kwargs)
        # Keep only the last 10 records for this charger
        logs = IPLog.objects.filter(charger=self.charger).order_by('-timestamp')
        if logs.count() > 10:
            logs[10:].delete()
