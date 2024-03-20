# remote_stop_transaction.py
from ocpp_app.models import ChargingSession
from django.utils.timezone import now

async def handle_remote_stop_transaction(payload):
    transaction_id = payload.get("transactionId")
    if not transaction_id:
        return {"status": "Rejected", "error": "MissingTransactionId"}

    session = ChargingSession.objects.filter(id=transaction_id).first()
    if session:
        session.end_time = now()
        session.save()
        return {"status": "Accepted"}
    else:
        return {"status": "Rejected", "error": "InvalidTransactionId"}
