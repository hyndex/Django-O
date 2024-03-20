from ocpp_app.models import ChargingSession, MeterValue


async def handle_metervalues(payload):
    transaction_id = payload.get("transactionId")
    if not transaction_id:
        return {"error": "MissingTransactionId"}

    meter_values = payload.get("meterValue", [])
    session = ChargingSession.objects.filter(id=transaction_id).first()

    if session:
        for meter_value in meter_values:
            timestamp = meter_value.get("timestamp")
            if not timestamp:
                continue  # Skip this meter value if timestamp is missing

            sampled_values = meter_value.get("sampledValue", [])

            for sampled_value in sampled_values:
                value = sampled_value.get("value")
                if value is None:
                    continue  # Skip this sampled value if value is missing

                context = sampled_value.get("context", "Unknown")
                format = sampled_value.get("format", "Unknown")
                measurand = sampled_value.get("measurand", "Unknown")
                location = sampled_value.get("location", "Unknown")
                unit = sampled_value.get("unit", "Unknown")

                # Create or update meter value
                MeterValue.objects.update_or_create(
                    session=session,
                    timestamp=timestamp,
                    defaults={
                        "value": value,
                        "context": context,
                        "format": format,
                        "measurand": measurand,
                        "location": location,
                        "unit": unit,
                    }
                )

        # Check if the session needs to be stopped based on meter values
        # and perform necessary actions

        return {}
    else:
        return {"error": "InvalidTransactionId"}

