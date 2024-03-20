# ocpp_app/message_handlers/handle_authorize.py
from ocpp_app.models import IdTag

def handle_authorize(payload):
    id_tag = payload.get("idTag")
    id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()
    if id_tag_obj and not id_tag_obj.is_blocked and not id_tag_obj.is_expired:
        return {"idTagInfo": {"status": "Accepted"}}
    else:
        return {"idTagInfo": {"status": "Blocked"}}
