import asyncio
from datetime import datetime, timedelta
from users.utils import send_sms, send_push_notification

class RemoteStartQueueManager:
    def __init__(self, timeout_minutes=5, reminder_minutes=2):
        self.queue = asyncio.Queue()
        self.timeout_minutes = timeout_minutes
        self.reminder_minutes = reminder_minutes
        self.tasks = {}

    async def add_to_queue(self, user, cpid, connector_id, id_tag):
        await self.queue.put((user, cpid, connector_id, id_tag))
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
        self.queue.task_done()
        del self.tasks[user.id]
        # Send timeout notification
        message = f"Your charging session at {cpid} has been cancelled due to inactivity."
        send_sms(user.profile.phone_number, message)
        send_push_notification(user, message)

    async def start_next_in_queue(self):
        if not self.queue.empty():
            user, cpid, connector_id, id_tag = await self.queue.get()
            # Start charging session
            response = await async_to_sync(cs_remote_start_transaction)(cpid, connector_id, id_tag)
            if response.get('status') == 'Accepted':
                # Cancel the timeout task
                task = self.tasks.get(user.id)
                if task:
                    task.cancel()
                    del self.tasks[user.id]
                self.queue.task_done()
                return response
        return {'error': 'Queue is empty or failed to start charging session'}

