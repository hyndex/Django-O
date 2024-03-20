# ocpp_app/message_handlers/handle_heartbeat.py
from ocpp_app.models import Charger

def handle_heartbeat(payload, charger_id):
    Charger.objects.filter(charger_id=charger_id).update(last_heartbeat=now())
    return {"currentTime": now().isoformat()}
