# ocpp_app/message_handlers/cs_remote_start_transaction.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_remote_start_transaction(cpid, connector_id, id_tag, charging_profile=None):
    action = "RemoteStartTransaction"
    payload = {
        "connectorId": connector_id,
        "idTag": id_tag,
        "chargingProfile": charging_profile
    }
    response = await send_ocpp_message_and_await_response(cpid, action, payload)
    return response
