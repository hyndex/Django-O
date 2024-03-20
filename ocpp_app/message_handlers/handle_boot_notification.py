from ocpp_app.models import Charger

async def handle_boot_notification(payload):
    charger_id = payload.get("chargerId")
    if not charger_id:
        return {"error": "MissingChargerId"}

    charger, created = Charger.objects.get_or_create(charger_id=charger_id)
    charger.last_heartbeat = now()
    charger.vendor = payload.get("chargePointVendor", "Unknown")
    charger.model = payload.get("chargePointModel", "Unknown")
    charger.save()
    return {"currentTime": now().isoformat(), "interval": 60, "status": "Accepted"}

    