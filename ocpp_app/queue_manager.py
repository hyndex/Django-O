import asyncio
import aioredis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ChargingSession, Connector
from users.utils import send_sms

class RemoteStartQueueManager:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        self.queue_name = "charging_queue"
        self.max_queue_size = 5
        self.timeout_minutes = 10

    async def add_to_queue(self, user_id, charger_id, connector_id, id_tag):
        queue_length = await self.redis.llen(self.queue_name)
        if queue_length >= self.max_queue_size:
            await self.notify_user(user_id, "The charging queue is full. Please try again later.")
            return False

        queue_item = f"{user_id},{charger_id},{connector_id},{id_tag}"
        await self.redis.rpush(self.queue_name, queue_item)
        await self.notify_users_in_queue()

        asyncio.create_task(self.remove_user_from_queue_after_timeout(queue_item))
        return True

    async def notify_user(self, user_id, message):
        user = await sync_to_async(User.objects.get)(id=user_id)
        send_sms(user.profile.phone_number, message)

    async def notify_users_in_queue(self):
        queue_length = await self.redis.llen(self.queue_name)
        for index in range(queue_length):
            user_id, *_ = (await self.redis.lindex(self.queue_name, index)).split(',')
            position = index + 1
            await self.notify_user(user_id, f"Your position in the charging queue is now {position}.")

    async def remove_user_from_queue_after_timeout(self, queue_item):
        await asyncio.sleep(self.timeout_minutes * 60)
        await self.redis.lrem(self.queue_name, 0, queue_item)
        user_id, *_ = queue_item.split(',')
        await self.notify_user(user_id, "You have been removed from the charging queue due to inactivity.")

    async def start_next_in_queue(self):
        if await self.redis.llen(self.queue_name) > 0:
            queue_item = await self.redis.lpop(self.queue_name)
            user_id, charger_id, connector_id, id_tag = queue_item.split(',')
            # Trigger charging session here. Ensure this function is properly implemented.
            await self.start_charging(charger_id, connector_id, id_tag)
            await self.notify_user(user_id, "Your charging session has started.")
