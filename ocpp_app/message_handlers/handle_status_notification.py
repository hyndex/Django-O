# ocpp_app/message_handlers/handle_status_notification.py
from ocpp_app.models import Connector
from asgiref.sync import sync_to_async

async def handle_status_notification(payload):
    connector_id = payload.get("connectorId")
    status = payload.get("status")
    # connector = Connector.objects.filter(id=connector_id).first()
    connector = await sync_to_async(Connector.objects.get, thread_sensitive=True)(id=connector_id)
    # connector=connector.first()
    if connector:
        connector.status = status
        # connector.save()
        await sync_to_async(connector.save, thread_sensitive=True)()
        return {}
    else:
        return {"error": "InvalidConnectorId"}
