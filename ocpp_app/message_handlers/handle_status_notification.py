# ocpp_app/message_handlers/handle_status_notification.py
from asgiref.sync import sync_to_async
from ocpp_app.models import Connector

async def handle_status_notification(payload):
    connector_id = payload.get("connectorId")
    status = payload.get("status")
    connector = await sync_to_async(Connector.objects.get, thread_sensitive=True)(id=connector_id)
    if connector:
        connector.status = status
        await sync_to_async(connector.save, thread_sensitive=True)()
        # Return a dictionary with the response payload
        return {"status": "Accepted"}
    else:
        raise ValueError("InvalidConnectorId")
