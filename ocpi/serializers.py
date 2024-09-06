from rest_framework import serializers
from .models import Charger, ChargingSession, SessionBilling, IdTag, Connector

class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = ['connector_id', 'status', 'type']

class ChargerSerializer(serializers.ModelSerializer):
    connectors = ConnectorSerializer(many=True, read_only=True)

    class Meta:
        model = Charger
        fields = ['id', 'charger_id', 'name', 'address', 'coordinates', 'type', 'connectors', 'price_per_kwh']

class ChargingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingSession
        fields = ['transaction_id', 'start_time', 'end_time', 'meter_start', 'meter_stop', 'connector', 'id_tag', 'reservation_id', 'auth_method']

class SessionBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionBilling
        fields = ['session', 'amount_consumed', 'kwh_consumed']

class IdTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdTag
        fields = ['idtag', 'user', 'is_blocked', 'expiry_date']

class RemoteStartTransactionSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=50)
    connectorId = serializers.IntegerField()
    idTag = serializers.CharField(max_length=50)

class RemoteStopTransactionSerializer(serializers.Serializer):
    chargerId = serializers.CharField(max_length=50)
    transactionId = serializers.IntegerField()
