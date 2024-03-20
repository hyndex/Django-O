# ocpp_app/message_handlers/handle_heartbeat.py
from django.utils.timezone import now
from ocpp_app.models import Charger

def handle_heartbeat(payload):
    # In a real implementation, you would update the last heartbeat timestamp for the charger
    return {"currentTime": now().isoformat()}
