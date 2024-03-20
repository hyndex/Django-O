# ocpp_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .ocpp_task_manager import OCPPTaskManager
from .ocpp_message_handler import OCPPMessageHandler

class OCPPConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.cpid = self.scope['url_route']['kwargs']['cpid']
        self.ocpp_task_manager = OCPPTaskManager(self.channel_name)
        self.ocpp_message_handler = OCPPMessageHandler()
        await self.accept()

    async def disconnect(self, close_code):
        pass  # Add any cleanup logic here

    async def receive(self, text_data):
        message = json.loads(text_data)
        message_type = message[0]

        if message_type == 2:  # CALL
            response = await self.ocpp_message_handler.handle_message(message)
            await self.send(response)
        elif message_type == 3:  # CALLRESULT
            self.ocpp_task_manager.handle_call_result(message[1], message[2])
        elif message_type == 4:  # CALLERROR
            self.ocpp_task_manager.handle_call_error(message[1], message[2], message[3], message[4])
