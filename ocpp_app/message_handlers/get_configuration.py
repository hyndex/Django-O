# ocpp_app/message_handlers/cs_get_configuration.py
from .ocpp_utils import send_ocpp_message_and_await_response

async def cs_get_configuration(cpid, key=None):
    action = "GetConfiguration"
    payload = {"key": key} if key else {}
    response = await send_ocpp_message_and_await_response(cpid, action, payload)

    # Assuming 'response' contains the list of configurations in its 'configurationKey' field.
    for config in response.get('configurationKey', []):
        key = config['key']
        value = config['value']
        readonly = config.get('readonly', False)

        # Update or create the ChargerConfig entry in the database
        ChargerConfig.objects.update_or_create(
            charger_id=cpid,  # Assuming 'charger_id' is a field linking to the charger entity
            key=key,
            defaults={'value': value, 'readonly': readonly}
        )

    return response