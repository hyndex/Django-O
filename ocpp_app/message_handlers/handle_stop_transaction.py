# ocpp_app/message_handlers/handle_stop_transaction.py
from asgiref.sync import sync_to_async
from ocpp_app.models import ChargingSession

async def handle_stop_transaction(payload):
    transaction_id = payload.get("transactionId")
    meter_stop = payload.get("meterStop")
    timestamp = payload.get("timestamp")
    reason = payload.get("reason")

    session = await sync_to_async(ChargingSession.objects.filter(transaction_id=transaction_id).first, thread_sensitive=True)()

    if session:
        session.end_time = timestamp
        session.meter_stop = meter_stop
        session.reason = reason
        await sync_to_async(session.save, thread_sensitive=True)()
        return {"idTagInfo": {"status": "Accepted"}}
    else:
        raise ValueError("InvalidTransactionId")