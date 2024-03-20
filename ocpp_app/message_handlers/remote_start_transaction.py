# remote_start_transaction.py
from ocpp_app.models import Connector, IdTag, ChargingSession
from django.utils.timezone import now

async def handle_remote_start_transaction(payload):
    connector_id = payload.get("connectorId")
    id_tag = payload.get("idTag")

    if not all([connector_id, id_tag]):
        return {"status": "Rejected", "error": "MissingRequiredFields"}

    connector = Connector.objects.filter(id=connector_id).first()
    id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()

    if connector and id_tag_obj:
        if connector.status != "Available":
            return {"status": "Rejected", "error": "ConnectorNotAvailable"}
        session = ChargingSession.objects.create(
            connector=connector,
            id_tag=id_tag_obj,
            start_time=now(),
            meter_start=0  # Assuming meter start at 0 for new session
        )
        return {"status": "Accepted", "transactionId": session.id}
    else:
        return {"status": "Rejected", "error": "InvalidConnectorIdOrIdTag"}
