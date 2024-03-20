# unlock_connector.py
from ocpp_app.models import Connector

async def handle_unlock_connector(payload):
    connector_id = payload.get("connectorId")
    if not connector_id:
        return {"status": "Rejected", "error": "MissingConnectorId"}

    connector = Connector.objects.filter(id=connector_id).first()
    if connector:
        # Implement logic to unlock the connector
        unlock_connector(connector_id)
        return {"status": "Accepted"}
    else:
        return {"status": "Rejected", "error": "InvalidConnectorId"}
