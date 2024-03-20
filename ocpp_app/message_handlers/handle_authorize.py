# ocpp_app/message_handlers/handle_authorize.py
from ocpp_app.models import IdTag

def handle_authorize(payload):
    id_tag = payload.get("idTag")
    id_tag_obj, created = IdTag.objects.get_or_create(idtag=id_tag)

    if id_tag_obj.is_blocked or id_tag_obj.is_expired:
        return {"idTagInfo": {"status": "Blocked"}}
    else:
        return {"idTagInfo": {"status": "Accepted"}}
