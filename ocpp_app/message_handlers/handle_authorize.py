# ocpp_app/message_handlers/handle_authorize.py
from asgiref.sync import sync_to_async
from ocpp.v16 import call_result
from ocpp_app.models import IdTag

async def handle_authorize(payload):
    id_tag = payload.get("idTag")
    id_tag_obj, created = await sync_to_async(IdTag.objects.get_or_create, thread_sensitive=True)(idtag=id_tag)

    if id_tag_obj.is_blocked or id_tag_obj.is_expired:
        return call_result.AuthorizePayload(idTagInfo={"status": "Blocked"})
    else:
        return call_result.AuthorizePayload(idTagInfo={"status": "Accepted"})
