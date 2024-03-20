# ocpp_app/message_handlers/handle_stop_transaction.py
from django.utils.timezone import now
from ocpp_app.models import ChargingSession

def handle_stop_transaction(payload):
    transaction_id = payload.get("transactionId")
    meter_stop = payload.get("meterStop")
    timestamp = payload.get("timestamp")

    session = ChargingSession.objects.filter(id=transaction_id).first()
    if session:
        session.end_time = timestamp
        session.meter_stop = meter_stop
        session.save()
        return {"idTagInfo": {"status": "Accepted"}}
    else:
        return {"error": "InvalidTransactionId"}
