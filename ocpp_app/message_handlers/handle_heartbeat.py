from ocpp_app.models import Charger

async def handle_heartbeat(payload):
    charger_id = payload.get("chargerId")
    if not charger_id:
        return {"error": "MissingChargerId"}

    charger = Charger.objects.filter(charger_id=charger_id).first()
    if charger:
        charger.last_heartbeat = now()
        charger.save()
        return {"currentTime": now().isoformat()}
    else:
        return {"error": "ChargerNotFound"}

    