from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Charger, IdTag, Connector
from .consumers import OCPPConsumer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    RemoteStartTransactionSerializer,
    RemoteStopTransactionSerializer,
    GetConfigurationSerializer,
    SetConfigurationSerializer,
    ClearCacheSerializer,
    ResetChargerSerializer,
)

def send_to_charger(charger_id, action, payload):
    channel_layer = get_channel_layer()
    try:
        response = async_to_sync(channel_layer.send)(
            f"charger_{charger_id}",
            {
                "type": action.lower(),
                "payload": payload
            }
        )
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

class RemoteStartTransactionView(APIView):
    def get(self, request):
        serializer = RemoteStartTransactionSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            connector_id = serializer.validated_data['connectorId']
            id_tag = serializer.validated_data['idTag']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            connector = Connector.objects.filter(charger__charger_id=charger_id, connector_id=connector_id).first()
            if not connector or connector.status != 'Available':
                return JsonResponse({'error': 'Invalid connector ID or connector not available'}, status=400)

            if not IdTag.objects.filter(idtag=id_tag).exists():
                return JsonResponse({'error': 'Invalid ID tag'}, status=400)

            return send_to_charger(
                charger_id,
                "RemoteStartTransaction",
                {
                    "connectorId": connector_id,
                    "idTag": id_tag,
                }
            )
        return Response(serializer.errors, status=400)

class RemoteStopTransactionView(APIView):
    def get(self, request):
        serializer = RemoteStopTransactionSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            transaction_id = serializer.validated_data['transactionId']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "RemoteStopTransaction",
                {
                    "transactionId": transaction_id,
                }
            )
        return Response(serializer.errors, status=400)

class GetConfigurationView(APIView):
    def get(self, request):
        serializer = GetConfigurationSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "GetConfiguration",
                {
                    "key": [serializer.validated_data.get('key')],
                }
            )
        return Response(serializer.errors, status=400)

class SetConfigurationView(APIView):
    def get(self, request):
        serializer = SetConfigurationSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "SetConfiguration",
                {
                    "key": serializer.validated_data['key'],
                    "value": serializer.validated_data['value'],
                }
            )
        return Response(serializer.errors, status=400)

class ClearCacheView(APIView):
    def get(self, request):
        serializer = ClearCacheSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "ClearCache",
                {}
            )
        return Response(serializer.errors, status=400)

class ResetChargerView(APIView):
    def get(self, request):
        serializer = ResetChargerSerializer(data=request.query_params)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            reset_type = serializer.validated_data['resetType']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "Reset",
                {
                    "type": reset_type,
                }
            )
        return Response(serializer.errors, status=400)

