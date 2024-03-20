# ocpp_app/message_handlers/cs_remote_stop_transaction.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_remote_stop_transaction(cpid, transaction_id):
    action = "RemoteStopTransaction"
    payload = {"transactionId": transaction_id}
    response = await send_ocpp_message_and_await_response(cpid, action, payload)
    return response

