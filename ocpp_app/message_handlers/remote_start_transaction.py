from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def remote_start_transaction(request):
    charger_id = request.GET.get('charger_id')
    connector_id = request.GET.get('connector_id')
    id_tag = request.GET.get('id_tag')

    # Prepare the payload for RemoteStartTransaction
    payload = {
        "connectorId": int(connector_id),
        "idTag": id_tag
    }

    # Get the channel layer and send a message to the consumer
    channel_layer = get_channel_layer()
    message = {
        "type": "send.call.message",
        "charger_id": charger_id,
        "action": "RemoteStartTransaction",
        "payload": payload
    }

    # Send the message and wait for the response
    response = async_to_sync(channel_layer.send)(f"ocpp_{charger_id}", message)
    return JsonResponse(response)
