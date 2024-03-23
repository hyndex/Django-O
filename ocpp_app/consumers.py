# import json
# import asyncio
# import uuid
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# import logging
# from .message_handlers.handle_authorize import handle_authorize
# from .message_handlers.handle_boot_notification import handle_boot_notification
# from .message_handlers.handle_heartbeat import handle_heartbeat
# from .message_handlers.handle_metervalues import handle_metervalues
# from .message_handlers.handle_start_transaction import handle_start_transaction
# from .message_handlers.handle_status_notification import handle_status_notification
# from .message_handlers.handle_stop_transaction import handle_stop_transaction

# from ocpp.v16.enums import Action

# logger = logging.getLogger(__name__)

# class OCPPConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.groups = []
#         self.handlers = {
#             Action.Authorize: handle_authorize,
#             Action.BootNotification: handle_boot_notification,
#             Action.Heartbeat: handle_heartbeat,
#             Action.MeterValues: handle_metervalues,
#             Action.StartTransaction: handle_start_transaction,
#             Action.StatusNotification: handle_status_notification,
#             Action.StopTransaction: handle_stop_transaction,        
#         }
#         self.action_handlers = {
#             "Authorize": handle_authorize,
#             "BootNotification": handle_boot_notification,
#             "Heartbeat": handle_heartbeat,
#             "MeterValues": handle_metervalues,
#             "StartTransaction": handle_start_transaction,
#             "StatusNotification": handle_status_notification,
#             "StopTransaction": handle_stop_transaction,
#             "RemoteStartTransaction": self.handle_remotestarttransaction,
#             "RemoteStopTransaction": self.handle_remotestoptransaction,
#             "GetConfiguration": self.handle_getconfiguration,
#             "SetConfiguration": self.handle_setconfiguration,
#             "ClearCache": self.handle_clearcache,
#             "Reset": self.handle_reset,
#             # Add more action handlers as needed
#         }

#     connected_chargers = set()
#     pending_calls = {}

#     async def connect(self):
#         self.subprotocol = self.scope.get('subprotocols', [])
#         if 'ocpp1.6j' in self.subprotocol or 'ocpp1.6' in self.subprotocol:
#             await self.accept(subprotocol=self.subprotocol[0])
#         else:
#             await self.close()
#         self.cpid = self.scope['url_route']['kwargs']['cpid']
#         self.connected_chargers.add(self.cpid)
#         logger.info(f"Connected charger: {self.cpid}")

#     async def disconnect(self, close_code):
#         self.connected_chargers.discard(self.cpid)
#         logger.info(f"Disconnected charger: {self.cpid}")

#     async def receive(self, text_data):
#         message = json.loads(text_data)
#         message_type, message_id = message[0], message[1]

#         try:
#             if message_type == 2:  # CALL
#                 action = message[2]
#                 payload = message[3]
#                 response = await self.handle_call(message_id, action, payload)
#                 if response:
#                     await self.send(json.dumps([3, message_id, response]))
#             elif message_type == 3:  # CALLRESULT
#                 await self.handle_call_result(message)
#             elif message_type == 4:  # CALLERROR
#                 await self.handle_call_error(message)
#         except Exception as e:
#             logger.error(f"Error processing message: {e}")

#     async def handle_call(self, message_id, action, payload):
#         # handler = getattr(self, f'handle_{action.lower()}', None)
#         handler = self.action_handlers.get(action)
#         if handler:
#             return await handler(payload)
#         else:
#             logger.warning(f"Unknown action: {action}")
#             return None

#     async def handle_call_result(self, message):
#         message_id = message[1]
#         if message_id in self.pending_calls:
#             future = self.pending_calls[message_id]
#             future.set_result(message[2])
#             del self.pending_calls[message_id]
#         else:
#             logger.warning(f"Received CALLRESULT for unknown message ID: {message_id}")

#     async def handle_call_error(self, message):
#         message_id = message[1]
#         if message_id in self.pending_calls:
#             future = self.pending_calls[message_id]
#             future.set_exception(Exception(f"CALLERROR: {message[2]} - {message[3]}"))
#             del self.pending_calls[message_id]
#         else:
#             logger.warning(f"Received CALLERROR for unknown message ID: {message_id}")

#     async def send_call_message_and_await_response(self, action, payload):
#         message_id = str(uuid.uuid4())
#         call_message = [2, message_id, action, payload]
#         future = asyncio.Future()
#         self.pending_calls[message_id] = future

#         await self.send(json.dumps(call_message))
#         try:
#             response_payload = await asyncio.wait_for(future, timeout=60)  # Wait for 60 seconds
#             return response_payload
#         except asyncio.TimeoutError:
#             logger.error(f"Timeout waiting for response to message ID: {message_id}")
#             del self.pending_calls[message_id]
#             raise

#     # Handler for RemoteStartTransaction
#     async def handle_remotestarttransaction(self, payload):
#         response = await self.send_call_message_and_await_response("RemoteStartTransaction", payload)
#         return response

#     # Handler for RemoteStopTransaction
#     async def handle_remotestoptransaction(self, payload):
#         response = await self.send_call_message_and_await_response("RemoteStopTransaction", payload)
#         return response

#     # Handler for GetConfiguration
#     async def handle_getconfiguration(self, payload):
#         response = await self.send_call_message_and_await_response("GetConfiguration", payload)
#         return response

#     # Handler for SetConfiguration
#     async def handle_setconfiguration(self, payload):
#         response = await self.send_call_message_and_await_response("SetConfiguration", payload)
#         return response

#     # Handler for ClearCache
#     async def handle_clearcache(self, payload):
#         response = await self.send_call_message_and_await_response("ClearCache", payload)
#         return response

#     # Handler for Reset
#     async def handle_reset(self, payload):
#         response = await self.send_call_message_and_await_response("Reset", payload)
#         return response




import json
import asyncio
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import logging
from .message_handlers.handle_authorize import handle_authorize
from .message_handlers.handle_boot_notification import handle_boot_notification
from .message_handlers.handle_heartbeat import handle_heartbeat
from .message_handlers.handle_metervalues import handle_metervalues
from .message_handlers.handle_start_transaction import handle_start_transaction
from .message_handlers.handle_status_notification import handle_status_notification
from .message_handlers.handle_stop_transaction import handle_stop_transaction

from ocpp.v16.enums import Action

logger = logging.getLogger(__name__)

class OCPPConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = []
        self.handlers = {
            Action.Authorize: handle_authorize,
            Action.BootNotification: handle_boot_notification,
            Action.Heartbeat: handle_heartbeat,
            Action.MeterValues: handle_metervalues,
            Action.StartTransaction: handle_start_transaction,
            Action.StatusNotification: handle_status_notification,
            Action.StopTransaction: handle_stop_transaction,        
        }
        self.action_handlers = {
            "Authorize": handle_authorize,
            "BootNotification": handle_boot_notification,
            "Heartbeat": handle_heartbeat,
            "MeterValues": handle_metervalues,
            "StartTransaction": handle_start_transaction,
            "StatusNotification": handle_status_notification,
            "StopTransaction": handle_stop_transaction,
            "RemoteStartTransaction": self.handle_remotestarttransaction,
            "RemoteStopTransaction": self.handle_remotestoptransaction,
            "GetConfiguration": self.handle_getconfiguration,
            "SetConfiguration": self.handle_setconfiguration,
            "ClearCache": self.handle_clearcache,
            "Reset": self.handle_reset,
            # Add more action handlers as needed
        }

    connected_chargers = set()
    pending_calls = {}

    async def connect(self):
        self.subprotocol = self.scope.get('subprotocols', [])
        if 'ocpp1.6j' in self.subprotocol or 'ocpp1.6' in self.subprotocol:
            await self.accept(subprotocol=self.subprotocol[0])
        else:
            await self.close()
        self.cpid = self.scope['url_route']['kwargs']['cpid']
        group_name = f"charger_{self.cpid}"  # Define group_name here
        await self.channel_layer.group_add(group_name, self.channel_name)
        print(f"Added {self.channel_name} to group {group_name}")
        self.connected_chargers.add(self.cpid)
        logger.info(f"Connected charger: {self.cpid}")

    async def disconnect(self, close_code):
        self.connected_chargers.discard(self.cpid)
        await self.channel_layer.group_discard(f"charger_{self.cpid}", self.channel_name)
        logger.info(f"Disconnected charger: {self.cpid}")

    async def receive(self, text_data):
        message = json.loads(text_data)
        message_type, message_id = message[0], message[1]

        try:
            if message_type == 2:  # CALL
                action = message[2]
                payload = message[3]
                response = await self.handle_call(message_id, action, payload)
                if response:
                    await self.send(json.dumps([3, message_id, response]))
            elif message_type == 3:  # CALLRESULT
                await self.handle_call_result(message)
            elif message_type == 4:  # CALLERROR
                await self.handle_call_error(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_call(self, message_id, action, payload):
        # handler = getattr(self, f'handle_{action.lower()}', None)
        handler = self.action_handlers.get(action)
        if handler:
            return await handler(payload)
        else:
            logger.warning(f"Unknown action: {action}")
            return None

    async def handle_call_result(self, message):
        message_id = message[1]
        if message_id in self.pending_calls:
            future = self.pending_calls[message_id]
            future.set_result(message[2])
            del self.pending_calls[message_id]
        else:
            logger.warning(f"Received CALLRESULT for unknown message ID: {message_id}")

    async def handle_call_error(self, message):
        message_id = message[1]
        if message_id in self.pending_calls:
            future = self.pending_calls[message_id]
            future.set_exception(Exception(f"CALLERROR: {message[2]} - {message[3]}"))
            del self.pending_calls[message_id]
        else:
            logger.warning(f"Received CALLERROR for unknown message ID: {message_id}")

    async def send_call_message_and_await_response(self, action, payload):
        message_id = str(uuid.uuid4())
        call_message = [2, message_id, action, payload]
        future = asyncio.Future()
        self.pending_calls[message_id] = future

        await self.send(json.dumps(call_message))
        try:
            response_payload = await asyncio.wait_for(future, timeout=60)  # Wait for 60 seconds
            return response_payload
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response to message ID: {message_id}")
            del self.pending_calls[message_id]
            raise

    # Handler for RemoteStartTransaction
    async def handle_remotestarttransaction(self, payload):
        response = await self.send_call_message_and_await_response("RemoteStartTransaction", payload)
        return response

    # Handler for RemoteStopTransaction
    async def handle_remotestoptransaction(self, payload):
        response = await self.send_call_message_and_await_response("RemoteStopTransaction", payload)
        return response

    # Handler for GetConfiguration
    async def handle_getconfiguration(self, payload):
        response = await self.send_call_message_and_await_response("GetConfiguration", payload)
        return response

    # Handler for SetConfiguration
    async def handle_setconfiguration(self, payload):
        response = await self.send_call_message_and_await_response("SetConfiguration", payload)
        return response

    # Handler for ClearCache
    async def handle_clearcache(self, payload):
        response = await self.send_call_message_and_await_response("ClearCache", payload)
        return response

    # Handler for Reset
    async def handle_reset(self, payload):
        response = await self.send_call_message_and_await_response("Reset", payload)
        return response

