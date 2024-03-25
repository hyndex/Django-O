import asyncio
from datetime import datetime, timedelta

import aioredis
from asgiref.sync import async_to_sync
from django.conf import settings

from .consumers import OCPPConsumer
from .models import Charger, Connector, IdTag
from .views import send_to_charger
from users.utils import send_sms, send_push_notification


class ChargerNotConnectedException(Exception):
    pass


class ConnectorUnavailableException(Exception):
    pass


class InvalidIdTagException(Exception):
    pass


def cs_remote_start_transaction(charger_id, connector_id, id_tag):
    if charger_id not in OCPPConsumer.connected_chargers or not Charger.objects.filter(charger_id=charger_id).exists():
        raise ChargerNotConnectedException('Charger not connected or invalid')

    connector = Connector.objects.filter(charger__charger_id=charger_id, connector_id=connector_id).first()
    if not connector or connector.status != 'Available':
        raise ConnectorUnavailableException('Invalid connector ID or connector not available')

    if not IdTag.objects.filter(idtag=id_tag).exists():
        raise InvalidIdTagException('Invalid ID tag')

    return send_to_charger(
        charger_id,
        "RemoteStartTransaction",
        {
            "connectorId": connector_id,
            "idTag": id_tag,
        }
    )


class RemoteStartQueueManager:
    def __init__(self, timeout_minutes=5, reminder_minutes=2):
        self.redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
        self.queue_name = "remote_start_queue"
        self.timeout_minutes = timeout_minutes
        self.reminder_minutes = reminder_minutes
        self.tasks = {}

    async def add_to_queue(self, user, cpid, connector_id, id_tag):
        queue_item = f"{user.id},{cpid},{connector_id},{id_tag}"
        await self.redis.rpush(self.queue_name, queue_item)
        task = asyncio.create_task(self.process_queue_item(user, cpid, connector_id, id_tag))
        self.tasks[user.id] = task

    async def process_queue_item(self, user, cpid, connector_id, id_tag):
        start_time = datetime.now()
        reminder_time = start_time + timedelta(minutes=self.reminder_minutes)
        end_time = start_time + timedelta(minutes=self.timeout_minutes)

        while datetime.now() < end_time:
            if datetime.now() > reminder_time:
                # Send reminder notification
                message = f"Your charging session at {cpid} is ready to start. Please start within the next {self.timeout_minutes - self.reminder_minutes} minutes."
                send_sms(user.profile.phone_number, message)
                send_push_notification(user, message)
            await asyncio.sleep(30)  # Check every 30 seconds

        # Remove from queue after timeout
        await self.redis.lrem(self.queue_name, 1, f"{user.id},{cpid},{connector_id},{id_tag}")
        del self.tasks[user.id]
        # Send timeout notification
        message = f"Your charging session at {cpid} has been cancelled due to inactivity."
        send_sms(user.profile.phone_number, message)
        send_push_notification(user, message)

    async def start_next_in_queue(self):
        if await self.redis.llen(self.queue_name) > 0:
            queue_item = await self.redis.lpop(self.queue_name)
            user_id, cpid, connector_id, id_tag = queue_item.split(',')
            # Start charging session
            response = await async_to_sync(cs_remote_start_transaction)(cpid, connector_id, id_tag)
            if response.get('status') == 'Accepted':
                # Cancel the timeout task
                task = self.tasks.get(int(user_id))
                if task:
                    task.cancel()
                    del self.tasks[int(user_id)]
                return response
        return {'error': 'Queue is empty or failed to start charging session'}
