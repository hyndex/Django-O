# change_availability.py
from ocpp_app.models import Connector

async def handle_change_availability(payload):
    connector_id = payload.get("connectorId")
    type = payload.get("type")
    if not all([connector_id, type]):
        return {"status": "Rejected", "error": "MissingRequiredFields"}

    connector = Connector.objects.filter(id=connector_id).first()
    if connector:
        if type in ["Operative", "Inoperative"]:
            connector.status = "Available" if type == "Operative" else "Unavailable"
            connector.save()
            return {"status": "Accepted"}
        else:
            return {"status": "Rejected", "error": "InvalidType"}
    else:
        return {"status": "Rejected", "error": "InvalidConnectorId"}
