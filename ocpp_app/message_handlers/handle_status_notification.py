from ocpp_app.models import Connector

async def handle_status_notification(payload):
    connector_id = payload.get("connectorId")
    status = payload.get("status")
    if not all([connector_id, status]):
        return {"error": "MissingRequiredFields"}

    connector = Connector.objects.filter(id=connector_id).first()
    if connector:
        connector.status = status
        connector.save()
        return {}
    else:
        return {"error": "InvalidConnectorId"}

