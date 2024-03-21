from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Charger, Connector

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
