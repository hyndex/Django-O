# ocpp_app/message_handlers/handle_heartbeat.py
from asgiref.sync import sync_to_async
from ocpp.v16 import call_result
from ocpp_app.models import Charger
from datetime import datetime

async def handle_heartbeat(charger_id):
    await sync_to_async(Charger.objects.filter, thread_sensitive=True)(charger_id=charger_id).update(last_heartbeat=datetime.now())
    return call_result.HeartbeatPayload(currentTime=datetime.now().isoformat())
