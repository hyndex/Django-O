# ocpp_app/message_handlers/cs_clear_cache.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_clear_cache(cpid):
    action = "ClearCache"
    payload = {}
    response = await send_ocpp_message_and_await_response(cpid, action, payload)
    return response
