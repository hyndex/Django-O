# ocpp_app/message_handlers/handle_boot_notification.py
from ocpp_app.models import Charger

def handle_boot_notification(payload):
    charger_id = payload.get("chargePointSerialNumber")
    vendor = payload.get("chargePointVendor")
    model = payload.get("chargePointModel")

    charger, created = Charger.objects.update_or_create(
        charger_id=charger_id,
        defaults={
            "vendor": vendor,
            "model": model,
            "last_heartbeat": now(),
        }
    )

    return {"status": "Accepted", "currentTime": now().isoformat(), "interval": 60}
