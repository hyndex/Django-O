# ocpp_app/message_handlers/handle_start_transaction.py
from ocpp_app.models import Connector, IdTag, ChargingSession

def handle_start_transaction(payload):
    connector_id = payload.get("connectorId")
    id_tag = payload.get("idTag")
    meter_start = payload.get("meterStart")
    timestamp = payload.get("timestamp")

    connector = Connector.objects.filter(id=connector_id).first()
    id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()

    if connector and id_tag_obj:
        session = ChargingSession.objects.create(
            connector=connector,
            id_tag=id_tag_obj,
            start_time=timestamp,
            meter_start=meter_start
        )
        return {"transactionId": session.id, "idTagInfo": {"status": "Accepted"}}
    else:
        return {"error": "InvalidConnectorIdOrIdTag"}
