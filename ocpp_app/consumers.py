# ocpp_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .ocpp_task_manager import OCPPTaskManager
from .ocpp_message_handler import OCPPMessageHandler
from asgiref.sync import async_to_sync
from .models import ChargingSession, MeterValues

class OCPPConsumer(AsyncWebsocketConsumer):
    connected_chargers = set()

    async def connect(self):
        self.cpid = self.scope['url_route']['kwargs']['cpid']
        self.ocpp_task_manager = OCPPTaskManager(self.channel_name)
        self.ocpp_message_handler = OCPPMessageHandler()
        await self.accept()
        self.connected_chargers.add(self.cpid)

    async def disconnect(self, close_code):
        self.connected_chargers.discard(self.cpid)


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




class MeterValueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"meter_values_user_{self.user.id}"

        # Find the ongoing charging session for the user
        id_tags = IdTag.objects.filter(user=self.user)
        self.charging_session = None
        for id_tag in id_tags:
            session = ChargingSession.objects.filter(id_tag=id_tag, end_time__isnull=True).first()
            if session:
                self.charging_session = session
                break

        if self.charging_session:
            # Join the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.charging_session:
            # Leave the group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "meter_values_message",
                "message": message
            }
        )

    # Receive message from the group
    async def meter_values_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message
        }))
