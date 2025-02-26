from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Charger, Connector
from rest_framework import serializers


class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = ['id', 'connector_id', 'status', 'type']

class ChargerSerializer(GeoFeatureModelSerializer):
    connectors = ConnectorSerializer(many=True, read_only=True)

    class Meta:
        model = Charger
        geo_field = 'coordinates'
        fields = ['id', 'charger_id', 'vendor', 'model', 'enabled', 'price_per_kwh', 'type', 'connectors']


class RemoteStartTransactionSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)
    connectorId = serializers.IntegerField()
    idTag = serializers.CharField(max_length=20)

class RemoteStopTransactionSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)
    transactionId = serializers.IntegerField()

class GetConfigurationSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)
    key = serializers.CharField(max_length=100, allow_blank=True, required=False)

class SetConfigurationSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)
    key = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=100)

class ClearCacheSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)

class ResetChargerSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=100)
    resetType = serializers.ChoiceField(choices=['Hard', 'Soft'])


class SendLocalListSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=20)
    listVersion = serializers.IntegerField(min_value=1)
    localAuthorizationList = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=20)
        )
    )

class ChangeAvailabilitySerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=20)
    connectorId = serializers.IntegerField(min_value=0)
    type = serializers.ChoiceField(choices=['Inoperative', 'Operative'])


class TriggerMessageSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=20)
    messageType = serializers.ChoiceField(choices=['BootNotification', 'StatusNotification', 'Heartbeat', 'MeterValues', 'FirmwareStatusNotification'])


class UpdateFirmwareSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=20)
    location = serializers.URLField()
    retrieveDate = serializers.DateTimeField()
