# change_configuration.py
from ocpp_app.models import ChargerConfig

async def handle_change_configuration(payload):
    key = payload.get("key")
    value = payload.get("value")
    if not all([key, value]):
        return {"status": "Rejected", "error": "MissingRequiredFields"}

    config = ChargerConfig.objects.filter(key=key).first()
    if config:
        if config.readonly:
            return {"status": "Rejected", "error": "ConfigurationReadOnly"}
        else:
            config.value = value
            config.save()
            return {"status": "Accepted"}
    else:
        return {"status": "Rejected", "error": "InvalidConfigurationKey"}
