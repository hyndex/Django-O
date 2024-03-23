# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# from asgiref.sync import async_to_sync
# import asyncio
# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point
# from .models import Charger
# from .serializers import ChargerSerializer
# from .models import Charger, Connector, IdTag, ChargingSession
# from .message_handlers import (
#     cs_change_availability,
#     cs_change_configuration,
#     cs_clear_cache,
#     cs_get_configuration,
#     cs_remote_start_transaction,
#     cs_remote_stop_transaction,
# )
# from .consumers import OCPPConsumer
# from .queue_manager import remote_start_queue_manager

# @require_POST
# @login_required
# def change_availability_view(request):
#     cpid = request.POST.get('cpid')
#     charger = Charger.objects.filter(charger_id=cpid).first()
#     if not charger or cpid not in OCPPConsumer.connected_chargers:
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     connector_id = int(request.POST.get('connectorId'))
#     if not charger.connectors.filter(connector_id=connector_id).exists():
#         return JsonResponse({'error': 'Invalid connector ID'}, status=400)

#     type = request.POST.get('type')
#     if type not in ['Operative', 'Inoperative']:
#         return JsonResponse({'error': 'Invalid type'}, status=400)

#     response = async_to_sync(cs_change_availability)(cpid, connector_id, type)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def change_configuration_view(request):
#     cpid = request.POST.get('cpid')
#     if cpid not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=cpid).exists():
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     key = request.POST.get('key')
#     value = request.POST.get('value')

#     response = async_to_sync(cs_change_configuration)(cpid, key, value)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def clear_cache_view(request):
#     cpid = request.POST.get('cpid')
#     if cpid not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=cpid).exists():
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     response = async_to_sync(cs_clear_cache)(cpid)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def get_configuration_view(request):
#     cpid = request.POST.get('cpid')
#     if cpid not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=cpid).exists():
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     key = request.POST.get('key', None)
#     response = async_to_sync(cs_get_configuration)(cpid, key)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def remote_start_transaction_view(request):
#     cpid = request.POST.get('cpid')
#     if cpid not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=cpid).exists():
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     connector_id = int(request.POST.get('connectorId'))
#     connector = Connector.objects.filter(charger__charger_id=cpid, connector_id=connector_id).first()
#     if not connector or connector.status != 'Available':
#         return JsonResponse({'error': 'Invalid connector ID or connector not available'}, status=400)

#     id_tag = request.POST.get('idTag')
#     if not IdTag.objects.filter(idtag=id_tag, user=request.user).exists():
#         return JsonResponse({'error': 'Invalid ID tag or not associated with the user'}, status=400)

#     response = async_to_sync(cs_remote_start_transaction)(cpid, connector_id, id_tag)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def remote_stop_transaction_view(request):
#     cpid = request.POST.get('cpid')
#     if cpid not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=cpid).exists():
#         return JsonResponse({'error': 'Charger not connected or invalid'}, status=400)

#     transaction_id = int(request.POST.get('transactionId'))
#     session = ChargingSession.objects.filter(id=transaction_id, connector__charger__charger_id=cpid).first()

#     if not session or session.id_tag.user != request.user:
#         return JsonResponse({'error': 'Invalid transaction ID or not associated with the user'}, status=400)
    
#     if session.status != 'Charging':
#         return JsonResponse({'error': 'Transaction is not active'}, status=400)

#     response = async_to_sync(cs_remote_stop_transaction)(cpid, transaction_id)
#     return JsonResponse(response)

# @require_POST
# @login_required
# def add_to_remote_start_queue(request):
#     cpid = request.POST.get('cpid')
#     connector_id = int(request.POST.get('connectorId'))
#     id_tag = request.POST.get('idTag')

#     asyncio.create_task(remote_start_queue_manager.add_to_queue(request.user, cpid, connector_id, id_tag))
#     return JsonResponse({'message': 'Added to remote start queue'})

# @require_POST
# @login_required
# def start_next_in_remote_start_queue(request):
#     response = asyncio.run(remote_start_queue_manager.start_next_in_queue())
#     return JsonResponse(response)

# @require_POST
# @login_required
# def check_remote_start_queue_status(request):
#     position = remote_start_queue_manager.get_user_position(request.user)
#     return JsonResponse({'position': position})

# @require_POST
# @login_required
# def remote_start_charge_with_queue(request):
#     cpid = request.POST.get('cpid')
#     connector_id = int(request.POST.get('connectorId'))
#     id_tag = request.POST.get('idTag')

#     if remote_start_queue_manager.is_queue_empty():
#         response = asyncio.run(remote_start_queue_manager.start_charging(request.user, cpid, connector_id, id_tag))
#         if response.get('status') == 'Accepted':
#             return JsonResponse({'message': 'Charging session started'})
#         else:
#             return JsonResponse({'error': 'Failed to start charging session'}, status=500)
#     else:
#         position = remote_start_queue_manager.get_user_position(request.user)
#         if position == 0:
#             asyncio.create_task(remote_start_queue_manager.add_to_queue(request.user, cpid, connector_id, id_tag))
#             return JsonResponse({'message': 'Added to remote start queue, you are in position 1'})
#         elif position == 1:
#             response = asyncio.run(remote_start_queue_manager.start_next_in_queue())
#             if response.get('status') == 'Accepted':
#                 return JsonResponse({'message': 'Charging session started'})
#             else:
#                 return JsonResponse({'error': 'Failed to start charging session'}, status=500)
#         else:
#             return JsonResponse({'message': f'You are in position {position} in the queue'})





# class ChargerViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Charger.objects.all()
#     serializer_class = ChargerSerializer

#     def get_queryset(self):
#         queryset = Charger.objects.all()
#         lat = self.request.query_params.get('lat')
#         lon = self.request.query_params.get('lon')
#         radius = self.request.query_params.get('radius')
#         connector_status = self.request.query_params.get('connector_status')
#         connector_type = self.request.query_params.get('connector_type')

#         if lat and lon:
#             point = Point(float(lon), float(lat))
#             queryset = queryset.annotate(distance=Distance('coordinates', point)).order_by('distance')

#             if radius:
#                 queryset = queryset.filter(coordinates__distance_lte=(point, radius))

#         if connector_status:
#             queryset = queryset.filter(connectors__status=connector_status)

#         if connector_type:
#             queryset = queryset.filter(connectors__type=connector_type)

#         return queryset

#     @action(detail=False, methods=['get'])
#     def search(self, request):
#         query = request.query_params.get('query')
#         queryset = self.get_queryset()

#         if query:
#             queryset = queryset.filter(model__icontains=query)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)