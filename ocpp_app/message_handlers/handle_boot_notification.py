# ocpp_app/message_handlers/handle_boot_notification.py
from asgiref.sync import sync_to_async
from ocpp.v16 import call_result
from ocpp_app.models import Charger
from datetime import datetime

async def handle_boot_notification(payload):
    charger_id = payload.get("chargePointSerialNumber")
    vendor = payload.get("chargePointVendor")
    model = payload.get("chargePointModel")

    charger, created = await sync_to_async(Charger.objects.update_or_create, thread_sensitive=True)(
        charger_id=charger_id,
        defaults={
            "vendor": vendor,
            "model": model,
            "last_heartbeat": datetime.now(),
        }
    )

    return call_result.BootNotificationPayload(
        status="Accepted",
        currentTime=datetime.now().isoformat(),
        interval=60
    )
