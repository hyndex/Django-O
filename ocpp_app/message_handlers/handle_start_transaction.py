# ocpp_app/message_handlers/handle_start_transaction.py
from asgiref.sync import sync_to_async
from ocpp.v16 import call_result
from ocpp_app.models import Connector, IdTag, ChargingSession

async def handle_start_transaction(payload):
    connector_id = payload.get("connectorId")
    id_tag = payload.get("idTag")
    meter_start = payload.get("meterStart")
    timestamp = payload.get("timestamp")

    connector = await sync_to_async(Connector.objects.filter, thread_sensitive=True)(id=connector_id).first()
    id_tag_obj = await sync_to_async(IdTag.objects.filter, thread_sensitive=True)(idtag=id_tag).first()

    if connector and id_tag_obj:
        session = await sync_to_async(ChargingSession.objects.create, thread_sensitive=True)(
            connector=connector,
            id_tag=id_tag_obj,
            start_time=timestamp,
            meter_start=meter_start
        )
        return call_result.StartTransactionPayload(transactionId=session.id, idTagInfo={"status": "Accepted"})
    else:
        raise ValueError("InvalidConnectorIdOrIdTag")
