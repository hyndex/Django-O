from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Charger, IdTag, Connector
from .consumers import OCPPConsumer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.gis.geos import Point
from rest_framework import viewsets
from django.contrib.gis.db.models.functions import Distance
from .serializers import (
    RemoteStartTransactionSerializer,
    RemoteStopTransactionSerializer,
    GetConfigurationSerializer,
    SetConfigurationSerializer,
    ClearCacheSerializer,
    ResetChargerSerializer,
    ChangeAvailabilitySerializer,
    TriggerMessageSerializer,
    UpdateFirmwareSerializer,
    SendLocalListSerializer
)
from .serializers import ChargerSerializer
import aioredis
from django.conf import settings
import json

redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_to_charger(charger_id, action, payload):
    channel_layer = get_channel_layer()
    group_name = f"charger_{charger_id}"  
    try:
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": action.lower(),
            "payload": payload
        })
        return JsonResponse({"status": "Message sent successfully"})
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


            limit = serializer.validated_data.get('limit')
            limit_type = serializer.validated_data.get('limitType')
            
            # Create a unique key for each charging session request to store limit and limit type temporarily
            redis_key = f"charging:{charger_id}:{connector_id}:{id_tag}"
            limit_info = json.dumps({'limit': limit, 'limit_type': limit_type})
            
            # Store the limit and limit type in Redis with an expiration time
            async_to_sync(redis.set)(redis_key, limit_info, ex=60)  # Expires in 60 seconds
            
            # Assuming send_to_charger is properly implemented to handle synchronous code
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
                "clearcache",
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


class ChangeAvailabilityView(APIView):
    def post(self, request):
        serializer = ChangeAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            connector_id = serializer.validated_data['connectorId']
            availability_type = serializer.validated_data['type']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "ChangeAvailability",
                {
                    "connectorId": connector_id,
                    "type": availability_type,
                }
            )
        return Response(serializer.errors, status=400)



class TriggerMessageView(APIView):
    def post(self, request):
        serializer = TriggerMessageSerializer(data=request.data)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            message_type = serializer.validated_data['messageType']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "TriggerMessage",
                {
                    "requestedMessage": message_type,
                }
            )
        return Response(serializer.errors, status=400)



class UpdateFirmwareView(APIView):
    def post(self, request):
        serializer = UpdateFirmwareSerializer(data=request.data)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            location = serializer.validated_data['location']
            retrieve_date = serializer.validated_data['retrieveDate']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "UpdateFirmware",
                {
                    "location": location,
                    "retrieveDate": retrieve_date,
                }
            )
        return Response(serializer.errors, status=400)



class GetLocalListVersionView(APIView):
    def get(self, request):
        charger_id = request.query_params.get('chargerId')

        if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
            return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

        return send_to_charger(
            charger_id,
            "GetLocalListVersion",
            {}
        )


class SendLocalListView(APIView):
    def post(self, request):
        serializer = SendLocalListSerializer(data=request.data)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            list_version = serializer.validated_data['listVersion']
            local_authorization_list = serializer.validated_data['localAuthorizationList']

            if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
                return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

            return send_to_charger(
                charger_id,
                "SendLocalList",
                {
                    "listVersion": list_version,
                    "localAuthorizationList": local_authorization_list,
                }
            )
        return Response(serializer.errors, status=400)



class ChargerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Charger.objects.all()
    serializer_class = ChargerSerializer

    def get_queryset(self):
        queryset = Charger.objects.all()
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius')
        connector_status = self.request.query_params.get('connector_status')
        connector_type = self.request.query_params.get('connector_type')

        if lat and lon:
            point = Point(float(lon), float(lat))
            queryset = queryset.annotate(distance=Distance('coordinates', point)).order_by('distance')

            if radius:
                queryset = queryset.filter(coordinates__distance_lte=(point, radius))

        if connector_status:
            queryset = queryset.filter(connectors__status=connector_status)

        if connector_type:
            queryset = queryset.filter(connectors__type=connector_type)

        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query')
        queryset = self.get_queryset()

        if query:
            queryset = queryset.filter(model__icontains=query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    


from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

from .serializers import RemoteStartTransactionSerializer
from .queue_manager import RemoteStartQueueManager
from .models import Charger, Connector, IdTag

# Initialize your RemoteStartQueueManager
queue_manager = RemoteStartQueueManager()

class StartChargingView(APIView):
    async def post(self, request):
        serializer = RemoteStartTransactionSerializer(data=request.data)
        if serializer.is_valid():
            charger_id = serializer.validated_data['chargerId']
            connector_id = serializer.validated_data['connectorId']
            id_tag = serializer.validated_data['idTag']

            # Check for charger connectivity and availability
            try:
                charger = await sync_to_async(Charger.objects.get)(charger_id=charger_id)
                if not charger.enabled or not charger.online:
                    return JsonResponse({'error': 'Charger is not online or not enabled.'}, status=400)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Charger not found.'}, status=404)

            try:
                connector = await sync_to_async(Connector.objects.get)(charger=charger, connector_id=connector_id)
                if connector.status != 'Available':
                    return JsonResponse({'error': 'Connector is not available.'}, status=400)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Connector not found.'}, status=404)

            try:
                idtag = await sync_to_async(IdTag.objects.get)(idtag=id_tag)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'ID tag is invalid or not found.'}, status=404)

            # Manage the charging queue
            queue_status = await queue_manager.add_to_queue(request.user.id, charger_id, connector_id, id_tag)

            if queue_status == 'added':
                return JsonResponse({'message': 'You have been added to the charging queue. You will be notified when it is your turn.'}, status=202)
            elif queue_status == 'full':
                return JsonResponse({'error': 'The charging queue is currently full. Please try again later.'}, status=429)
            elif queue_status == 'active':
                return JsonResponse({'message': 'Charging is starting for your vehicle.'}, status=200)
            else:
                return JsonResponse({'error': 'Unexpected error occurred. Please try again.'}, status=500)

        return Response(serializer.errors, status=400)
