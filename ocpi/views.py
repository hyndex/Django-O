from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.authentication import BaseAuthentication
from .serializers import (
    ChargerSerializer, ChargingSessionSerializer, IdTagSerializer,
    SessionBillingSerializer, RemoteStartTransactionSerializer, RemoteStopTransactionSerializer
)
from ocpp_app.models import Charger, ChargingSession, IdTag, SessionBilling, Connector
from ocpp_app.queue_manager import RemoteStartQueueManager
from ocpp_app.consumers import OCPPConsumer
from django.contrib.auth.models import User


# Initialize the RemoteStartQueueManager
queue_manager = RemoteStartQueueManager()

# OCPI Token Authentication
class OCPITokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Token '):
            raise AuthenticationFailed('No valid OCPI token found.')

        token = token.split('Token ')[1]
        user = User.objects.filter(profile__ocpi_token=token).first()

        if not user or user.profile.ocpi_role not in ['CPO', 'eMSP']:
            raise AuthenticationFailed('Invalid OCPI token or role.')

        return (user, token)



# OCPI Versions View
class OCPIVersionsView(APIView):
    def get(self, request):
        versions = [{"version": "2.2", "url": request.build_absolute_uri('/ocpi/2.2/')}]
        return Response({"versions": versions}, status=status.HTTP_200_OK)


# OCPI Charger Location View (Only CPOs can manage their chargers)
class OCPIChargerLocationView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    def get(self, request):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can manage chargers.')
        
        chargers = Charger.objects.filter(publish_to_ocpi=True, party_id=request.user.profile.ocpi_party_id)
        serializer = ChargerSerializer(chargers, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)



# OCPI Session View (CPO manages sessions for their chargers)
class OCPISessionView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    # def post(self, request):
    #     if request.user.profile.ocpi_role != 'CPO':
    #         raise PermissionDenied('Only CPOs can manage sessions.')

    #     serializer = ChargingSessionSerializer(data=request.data)
    #     if serializer.is_valid():
    #         session = serializer.save(party_id=request.user.profile.ocpi_party_id)
    #         return Response({
    #             "status_code": 1000,
    #             "status_message": "Session started successfully",
    #             "data": serializer.data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, session_id):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can manage sessions.')

        session = ChargingSession.objects.filter(transaction_id=session_id, party_id=request.user.profile.ocpi_party_id).first()
        if session:
            serializer = ChargingSessionSerializer(session)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "Session not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, session_id):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can manage sessions.')

        session = ChargingSession.objects.filter(transaction_id=session_id, party_id=request.user.profile.ocpi_party_id).first()
        if session:
            session.end_time = timezone.now()
            session.save()
            return Response({"status": "Session stopped"}, status=status.HTTP_200_OK)
        return Response({"error": "Session not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)


# OCPI CDR View (CPO sends Charge Detail Records to eMSP)
class OCPICDRView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    # def post(self, request):
    #     if request.user.profile.ocpi_role != 'CPO':
    #         raise PermissionDenied('Only CPOs can manage CDRs.')

    #     serializer = SessionBillingSerializer(data=request.data)
    #     if serializer.is_valid():
    #         billing = serializer.save()
    #         billing.cdr_sent = True
    #         billing.save()
    #         return Response({
    #             "status_code": 1000,
    #             "status_message": "CDR accepted successfully"
    #         }, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can access billing data.')

        billing = SessionBilling.objects.filter(session__connector__charger__party_id=request.user.profile.ocpi_party_id)
        serializer = SessionBillingSerializer(billing, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)



# OCPI Token View (CRUD operations on tokens)
class OCPITokenView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    def get(self, request, token_uid):
        token = IdTag.objects.filter(idtag=token_uid, user__profile__ocpi_party_id=request.user.profile.ocpi_party_id).first()
        if token:
            serializer = IdTagSerializer(token)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "Token not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if request.user.profile.ocpi_role != 'eMSP':
            raise PermissionDenied('Only eMSPs can manage tokens.')

        serializer = IdTagSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.save(user=request.user)
            return Response({"data": IdTagSerializer(token).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, token_uid):
        if request.user.profile.ocpi_role != 'eMSP':
            raise PermissionDenied('Only eMSPs can manage tokens.')

        token = IdTag.objects.filter(idtag=token_uid, user__profile__ocpi_party_id=request.user.profile.ocpi_party_id).first()
        if not token:
            return Response({"error": "Token not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)

        serializer = IdTagSerializer(token, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, token_uid):
        if request.user.profile.ocpi_role != 'eMSP':
            raise PermissionDenied('Only eMSPs can manage tokens.')

        token = IdTag.objects.filter(idtag=token_uid, user__profile__ocpi_party_id=request.user.profile.ocpi_party_id).first()
        if token:
            token.delete()
            return Response({"message": "Token deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Token not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)


# OCPI Tariffs Viewclass OCPITariffsView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    def get(self, request):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can manage tariffs.')

        chargers = Charger.objects.filter(publish_to_ocpi=True, party_id=request.user.profile.ocpi_party_id)
        tariffs = []
        for charger in chargers:
            tariff = {
                "id": charger.id,
                "currency": "USD",
                "price_per_kwh": charger.price_per_kwh,
                "fixed_price": 0.0,
                "time_based_fee": 0.0,
                "tariff_type": "ENERGY"
            }
            tariffs.append(tariff)
        return Response({"data": tariffs}, status=status.HTTP_200_OK)



# OCPI Commands View (Start and Stop Sessions, using Queue Manager)
class OCPICommandsView(APIView):
    authentication_classes = [OCPITokenAuthentication]

    async def post(self, request, command):
        if request.user.profile.ocpi_role != 'CPO':
            raise PermissionDenied('Only CPOs can start or stop sessions.')
        if command == "START_SESSION":
            serializer = RemoteStartTransactionSerializer(data=request.data)
            if serializer.is_valid():
                charger_id = serializer.validated_data['chargerId']
                connector_id = serializer.validated_data['connectorId']
                id_tag = serializer.validated_data['idTag']

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

                # Add the user to the charging queue
                queue_status = await queue_manager.add_to_queue(request.user.id, charger_id, connector_id, id_tag)

                if queue_status == 'added':
                    return JsonResponse({'message': 'You have been added to the charging queue. You will be notified when it is your turn.'}, status=202)
                elif queue_status == 'full':
                    return JsonResponse({'error': 'The charging queue is currently full. Please try again later.'}, status=429)
                elif queue_status == 'active':
                    session_data = {
                        'connector': connector.id,
                        'id_tag': idtag.id,
                        'start_time': timezone.now(),
                        'meter_start': 0
                    }
                    session_serializer = ChargingSessionSerializer(data=session_data)
                    if session_serializer.is_valid():
                        session_serializer.save()
                        return JsonResponse({'message': 'Session started successfully.'}, status=200)
                    return JsonResponse({'error': session_serializer.errors}, status=500)
                return JsonResponse({'error': 'Unexpected error.'}, status=500)

            return Response(serializer.errors, status=400)

        elif command == "STOP_SESSION":
            serializer = RemoteStopTransactionSerializer(data=request.data)
            if serializer.is_valid():
                charger_id = serializer.validated_data['chargerId']
                transaction_id = serializer.validated_data['transactionId']

                try:
                    session = await sync_to_async(ChargingSession.objects.get)(transaction_id=transaction_id, end_time__isnull=True)
                except ObjectDoesNotExist:
                    return JsonResponse({'error': 'Transaction not found or already ended.'}, status=404)

                session.end_time = timezone.now()
                session.meter_stop = session.meter_start + 1000  # Example meter stop for the session
                session.save()

                return JsonResponse({'message': 'Session stopped successfully.'}, status=200)
            return Response(serializer.errors, status=400)

        return Response({"error": "Invalid command"}, status=status.HTTP_400_BAD_REQUEST)
