from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

async def cs_clear_cache(cpid):
    action = "ClearCache"
    payload = {}

    channel_layer = get_channel_layer()
    channel_name = f"charger_{cpid}"
    message = {
        "type": "send.call.message.and.await.response",
        "action": action,
        "payload": payload
    }

    # Send the message to the OCPPConsumer and await the response
    response = await async_to_sync(channel_layer.send)(channel_name, message)
    return response
