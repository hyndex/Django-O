# ocpp_app/message_handlers/handle_authorize.py
from asgiref.sync import sync_to_async
from ocpp_app.models import IdTag

async def handle_authorize(payload):
    id_tag = payload.get("idTag")
    id_tag_obj = await sync_to_async(IdTag.objects.filter(idtag=id_tag).first, thread_sensitive=True)()

    if id_tag_obj:
        if id_tag_obj.is_blocked or id_tag_obj.is_expired:
            return {"idTagInfo": {"status": "Blocked"}}
        else:
            return {"idTagInfo": {"status": "Accepted"}}
    else:
        # Handle the case when the IdTag does not exist in the database
        return {"idTagInfo": {"status": "Unknown"}}
