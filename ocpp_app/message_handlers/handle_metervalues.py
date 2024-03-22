# ocpp_app/message_handlers/handle_metervalues.py
from asgiref.sync import sync_to_async
from ocpp.v16 import call_result
from ocpp_app.models import ChargingSession, MeterValues

async def handle_metervalues(payload):
    transaction_id = payload.get("transactionId")
    meter_values = payload.get("MeterValues", [])
    session = await sync_to_async(ChargingSession.objects.filter, thread_sensitive=True)(transaction_id=transaction_id).first()

    if session:
        for meter_value in meter_values:
            timestamp = meter_value.get("timestamp")
            sampled_values = meter_value.get("sampledValue", [])
            for sampled_value in sampled_values:
                await sync_to_async(MeterValues.objects.create, thread_sensitive=True)(
                    charging_session=session,
                    timestamp=timestamp,
                    value=sampled_value.get("value"),
                    unit=sampled_value.get("unit"),
                    format=sampled_value.get("format"),
                    context=sampled_value.get("context"),
                    measurand=sampled_value.get("measurand"),
                    location=sampled_value.get("location"),
                )
        return call_result.MeterValuesPayload()
    else:
        raise ValueError("InvalidTransactionId")
