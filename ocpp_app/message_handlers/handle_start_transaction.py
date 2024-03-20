from ocpp_app.models import IdTag, Connector, ChargingSession


async def handle_start_transaction(payload):
    connector_id = payload.get("connectorId")
    id_tag = payload.get("idTag")
    meter_start = payload.get("meterStart")
    timestamp = payload.get("timestamp")

    if not all([connector_id, id_tag, meter_start, timestamp]):
        return {"error": "MissingRequiredFields"}

    id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()
    if not id_tag_obj:
        return {"idTagInfo": {"status": "Invalid"}}

    connector = Connector.objects.filter(id=connector_id).first()
    if connector:
        session = ChargingSession.objects.create(
            connector=connector,
            id_tag=id_tag_obj,
            start_time=timestamp,
            meter_start=meter_start
        )
        return {"transactionId": session.id, "idTagInfo": {"status": "Accepted"}}
    else:
        return {"error": "InvalidConnectorId"}

