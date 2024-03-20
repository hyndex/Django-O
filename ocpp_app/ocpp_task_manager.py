# ocpp_app/ocpp_task_manager.py
import json
import uuid
import asyncio
from channels.layers import get_channel_layer

class OCPPTaskManager:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel_layer = get_channel_layer()
        self.pending_calls = {}

    async def send_message(self, message):
        await self.channel_layer.send(
            self.channel_name,
            {
                "type": "ocpp.message",
                "message": message
            }
        )

    async def send_call(self, action, payload):
        message_id = str(uuid.uuid4())
        message = json.dumps([2, message_id, action, payload])
        await self.send_message(message)

        # Create a future to wait for the call result
        future = asyncio.Future()
        self.pending_calls[message_id] = future

        try:
            # Wait for the result with a timeout (e.g., 60 seconds)
            result = await asyncio.wait_for(future, timeout=60)
            return result
        except asyncio.TimeoutError:
            return {"error": "Timeout waiting for response"}
        finally:
            # Clean up the pending call
            del self.pending_calls[message_id]

    def handle_call_result(self, message_id, payload):
        future = self.pending_calls.get(message_id)
        if future and not future.done():
            future.set_result(payload)

    def handle_call_error(self, message_id, error_code, error_description, error_details):
        future = self.pending_calls.get(message_id)
        if future and not future.done():
            future.set_exception(Exception(f"{error_code} - {error_description}, Details: {error_details}"))
