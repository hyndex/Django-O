from rest_framework import serializers
from .models import PowerPlant, EnergyGenerationLog

class PowerPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerPlant
        fields = '__all__'

class EnergyGenerationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyGenerationLog
        fields = '__all__'
