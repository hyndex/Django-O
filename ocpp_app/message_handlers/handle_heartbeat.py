# ocpp_app/message_handlers/handle_heartbeat.py
from asgiref.sync import sync_to_async
from ocpp_app.models import Charger
from datetime import datetime
from django.utils import timezone

async def handle_heartbeat(charger_id):
    charger_queryset = Charger.objects.filter(charger_id=charger_id)
    await sync_to_async(charger_queryset.update, thread_sensitive=True)(last_heartbeat=timezone.now())
    return {"currentTime": timezone.now().isoformat()}
