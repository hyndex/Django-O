# ocpp_app/message_handlers/handle_boot_notification.py
from django.utils.timezone import now
from ocpp_app.models import Charger

def handle_boot_notification(payload):
    charger_id = payload.get("chargePointSerialNumber")
    charger, created = Charger.objects.get_or_create(charger_id=charger_id)
    charger.vendor = payload.get("chargePointVendor")
    charger.model = payload.get("chargePointModel")
    charger.last_heartbeat = now()
    charger.save()
    return {
        "status": "Accepted",
        "currentTime": now().isoformat(),
        "interval": 300  # Heartbeat interval in seconds
    }
