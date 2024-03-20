# ocpp_app/message_handlers/cs_change_configuration.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_change_configuration(cpid, key, value):
    action = "ChangeConfiguration"
    payload = {
        "key": key,
        "value": value
    }
    response = await send_ocpp_message_and_await_response(cpid, action, payload)
    return response
