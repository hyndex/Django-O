# views.py
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

def remote_start_transaction(request):
    charger_id = request.GET.get('chargerId')
    connector_id = request.GET.get('connectorId')
    id_tag = request.GET.get('idTag')

    payload = {
        "connectorId": connector_id,
        "idTag": id_tag,
    }

    return send_to_charger(charger_id, "RemoteStartTransaction", payload)

def remote_stop_transaction(request):
    charger_id = request.GET.get('chargerId')
    transaction_id = request.GET.get('transactionId')

    payload = {
        "transactionId": transaction_id,
    }

    return send_to_charger(charger_id, "RemoteStopTransaction", payload)

def get_configuration(request):
    charger_id = request.GET.get('chargerId')
    key = request.GET.get('key')

    payload = {
        "key": [key],
    }

    return send_to_charger(charger_id, "GetConfiguration", payload)

def set_configuration(request):
    charger_id = request.GET.get('chargerId')
    key = request.GET.get('key')
    value = request.GET.get('value')

    payload = {
        "key": key,
        "value": value,
    }

    return send_to_charger(charger_id, "SetConfiguration", payload)

def clear_cache(request):
    charger_id = request.GET.get('chargerId')

    return send_to_charger(charger_id, "ClearCache", {})

def reset_charger(request):
    charger_id = request.GET.get('chargerId')
    reset_type = request.GET.get('resetType')

    payload = {
        "type": reset_type,
    }

    return send_to_charger(charger_id, "Reset", payload)
