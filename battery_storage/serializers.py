from rest_framework import serializers
from .models import BatteryStorage, BatteryUsageLog

class BatteryStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryStorage
        fields = '__all__'

class BatteryUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryUsageLog
        fields = '__all__'
