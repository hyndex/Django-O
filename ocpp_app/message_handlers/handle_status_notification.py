# ocpp_app/message_handlers/handle_status_notification.py
from ocpp_app.models import Connector

def handle_status_notification(payload):
    connector_id = payload.get("connectorId")
    status = payload.get("status")
    connector = Connector.objects.filter(id=connector_id).first()
    if connector:
        connector.status = status
        connector.save()
        return {}
    else:
        return {"error": "InvalidConnectorId"}
