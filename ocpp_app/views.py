# ocpp_app/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from asgiref.sync import async_to_sync
from .message_handlers.cs_change_availability import cs_change_availability
from .message_handlers.cs_change_configuration import cs_change_configuration
from .message_handlers.cs_clear_cache import cs_clear_cache
from .message_handlers.cs_get_configuration import cs_get_configuration
from .message_handlers.cs_remote_start_transaction import cs_remote_start_transaction
from .message_handlers.cs_remote_stop_transaction import cs_remote_stop_transaction

@require_POST
def change_availability_view(request):
    cpid = request.POST.get('cpid')
    connector_id = int(request.POST.get('connectorId'))
    type = request.POST.get('type')
    response = async_to_sync(cs_change_availability)(cpid, connector_id, type)
    return JsonResponse(response)

@require_POST
def change_configuration_view(request):
    cpid = request.POST.get('cpid')
    key = request.POST.get('key')
    value = request.POST.get('value')
    response = async_to_sync(cs_change_configuration)(cpid, key, value)
    return JsonResponse(response)

@require_POST
def clear_cache_view(request):
    cpid = request.POST.get('cpid')
    response = async_to_sync(cs_clear_cache)(cpid)
    return JsonResponse(response)

@require_POST
def get_configuration_view(request):
    cpid = request.POST.get('cpid')
    key = request.POST.get('key', None)
    response = async_to_sync(cs_get_configuration)(cpid, key)
    return JsonResponse(response)

@require_POST
def remote_start_transaction_view(request):
    cpid = request.POST.get('cpid')
    connector_id = int(request.POST.get('connectorId'))
    id_tag = request.POST.get('idTag')
    response = async_to_sync(cs_remote_start_transaction)(cpid, connector_id, id_tag)
    return JsonResponse(response)

@require_POST
def remote_stop_transaction_view(request):
    cpid = request.POST.get('cpid')
    transaction_id = int(request.POST.get('transactionId'))
    response = async_to_sync(cs_remote_stop_transaction)(cpid, transaction_id)
    return JsonResponse(response)
