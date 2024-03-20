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
                value = sampled_value.get("value")
                MeterValue.objects.create(
                    session=session,
                    timestamp=timestamp,
                    value=value
                )
        return {}
    else:
        return {"error": "InvalidTransactionId"}
