# ocpp_app/ocpp_message_handler.py
import json
import asyncio
from ocpp.v16.enums import Action

from .message_handlers.handle_authorize import handle_authorize
from .message_handlers.handle_boot_notification import handle_boot_notification
from .message_handlers.handle_heartbeat import handle_heartbeat
from .message_handlers.handle_metervalues import handle_metervalues
from .message_handlers.handle_start_transaction import handle_start_transaction
from .message_handlers.handle_status_notification import handle_status_notification
from .message_handlers.handle_stop_transaction import handle_stop_transaction


class OCPPMessageHandler:
    def __init__(self):
        self.call_results = {}
        self.call_errors = {}

        self.handlers = {
            Action.Authorize: handle_authorize,
            Action.BootNotification: handle_boot_notification,
            Action.Heartbeat: handle_heartbeat,
            Action.MeterValues: handle_metervalues,
            Action.StartTransaction: handle_start_transaction,
            Action.StatusNotification: handle_status_notification,
            Action.StopTransaction: handle_stop_transaction,
            # Add other handlers as needed
        }

    async def handle_message(self, parsed_message):
        # parsed_message = json.loads(message)
        message_type = parsed_message[0]

        if message_type == 2:  # CALL
            return await self.handle_call(parsed_message)
        elif message_type == 3:  # CALLRESULT
            return self.handle_call_result(parsed_message)
        elif message_type == 4:  # CALLERROR
            return self.handle_call_error(parsed_message)
        else:
            print("Unknown message type:", message_type)
            return None

    async def handle_call(self, message):
        message_id, action, payload = message[1], message[2], message[3]
        handler = self.handlers.get(action)
        if handler:
            response_payload = await handler(payload)
            future = asyncio.Future()
            self.call_results[message_id] = future
            try:
                await asyncio.wait_for(future, timeout=60)  # Wait for 60 seconds for the result
                result_payload = future.result()
                return json.dumps([3, message_id, result_payload])
            except asyncio.TimeoutError:
                print(f"Timeout waiting for CALLRESULT for message ID {message_id}")
                return json.dumps([4, message_id, "Timeout", "No response received in time", {}])
            finally:
                del self.call_results[message_id]
        else:
            print(f"No handler for action: {action}")
            return json.dumps([4, message_id, "NotImplemented", f"No handler for action: {action}", {}])

    def handle_call_result(self, message):
        message_id, payload = message[1], message[2]
        future = self.call_results.get(message_id)
        if future and not future.done():
            future.set_result(payload)
        else:
            print(f"No pending CALL for message ID {message_id}")

    def handle_call_error(self, message):
        message_id, error_code, error_description, error_details = message[1], message[2], message[3], message[4]
        future = self.call_results.get(message_id)
        if future and not future.done():
            future.set_exception(Exception(f"{error_code} - {error_description}, Details: {error_details}"))
        else:
            print(f"No pending CALL for message ID {message_id}")
