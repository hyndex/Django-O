# ocpp_app/message_handlers/handle_metervalues.py
from ocpp_app.models import ChargingSession, MeterValue

def handle_metervalues(payload):
    transaction_id = payload.get("transactionId")
    meter_values = payload.get("meterValue", [])
    session = ChargingSession.objects.filter(transaction_id=transaction_id).first()

    if session:
        for meter_value in meter_values:
            timestamp = meter_value.get("timestamp")
            sampled_values = meter_value.get("sampledValue", [])
            for sampled_value in sampled_values:
                MeterValue.objects.create(
                    charging_session=session,
                    timestamp=timestamp,
                    value=sampled_value.get("value"),
                    unit=sampled_value.get("unit"),
                    format=sampled_value.get("format"),
                    context=sampled_value.get("context"),
                    measurand=sampled_value.get("measurand"),
                    location=sampled_value.get("location"),
                )
        return {}
    else:
        return {"error": "InvalidTransactionId"}
