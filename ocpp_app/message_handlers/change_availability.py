# ocpp_app/message_handlers/cs_change_availability.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_change_availability(cpid, connector_id, type):
    action = "ChangeAvailability"
    payload = {
        "connectorId": connector_id,
        "type": type
    }
    response = await send_ocpp_message_and_await_response(cpid, action, payload)
    return response
