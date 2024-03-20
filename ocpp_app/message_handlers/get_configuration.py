# get_configuration.py
from ocpp_app.models import ChargerConfig

async def handle_get_configuration(payload):
    key = payload.get("key")
    if key:
        config = ChargerConfig.objects.filter(key=key).first()
        if config:
            return {"status": "Accepted", "configurationKey": [{"key": config.key, "value": config.value, "readonly": config.readonly}]}
        else:
            return {"status": "Rejected", "error": "InvalidConfigurationKey"}
    else:
        configs = ChargerConfig.objects.all()
        return {"status": "Accepted", "configurationKey": [{"key": config.key, "value": config.value, "readonly": config.readonly} for config in configs]}
