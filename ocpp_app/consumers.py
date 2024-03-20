import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Charger, Connector, ChargingSession, IdTag
from django.utils.timezone import now

class OCPPConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        response = await self.handle_ocpp_message(data)
        await self.send(text_data=json.dumps(response))

    async def handle_ocpp_message(self, message):
        action = message.get("action")
        payload = message.get("payload", {})

        if action == "BootNotification":
            return await self.handle_boot_notification(payload)
        elif action == "Heartbeat":
            return await self.handle_heartbeat(payload)
        elif action == "Authorize":
            return await self.handle_authorize(payload)
        elif action == "StartTransaction":
            return await self.handle_start_transaction(payload)
        elif action == "StopTransaction":
            return await self.handle_stop_transaction(payload)
        elif action == "StatusNotification":
            return await self.handle_status_notification(payload)
        elif action == "MeterValues":
            return await self.handle_metervalues(payload)
        else:
            return {"status": "NotImplemented"}

    async def handle_authorize(self, payload):
        id_tag = payload.get("idTag")
        if not id_tag:
            return {"error": "MissingIdTag"}

        id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()
        if id_tag_obj and not id_tag_obj.is_blocked and not id_tag_obj.is_expired:
            return {"idTagInfo": {"status": "Accepted"}}
        else:
            return {"idTagInfo": {"status": "Blocked"}}

    async def handle_boot_notification(self, payload):
        charger_id = payload.get("chargerId")
        if not charger_id:
            return {"error": "MissingChargerId"}

        charger, created = Charger.objects.get_or_create(charger_id=charger_id)
        charger.last_heartbeat = now()
        charger.vendor = payload.get("chargePointVendor", "Unknown")
        charger.model = payload.get("chargePointModel", "Unknown")
        charger.save()
        return {"currentTime": now().isoformat(), "interval": 60, "status": "Accepted"}

    async def handle_heartbeat(self, payload):
        charger_id = payload.get("chargerId")
        if not charger_id:
            return {"error": "MissingChargerId"}

        charger = Charger.objects.filter(charger_id=charger_id).first()
        if charger:
            charger.last_heartbeat = now()
            charger.save()
            return {"currentTime": now().isoformat()}
        else:
            return {"error": "ChargerNotFound"}

    async def handle_metervalues(self, payload):
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

    async def handle_start_transaction(self, payload):
        connector_id = payload.get("connectorId")
        id_tag = payload.get("idTag")
        meter_start = payload.get("meterStart")
        timestamp = payload.get("timestamp")

        if not all([connector_id, id_tag, meter_start, timestamp]):
            return {"error": "MissingRequiredFields"}

        id_tag_obj = IdTag.objects.filter(idtag=id_tag).first()
        if not id_tag_obj:
            return {"idTagInfo": {"status": "Invalid"}}

        connector = Connector.objects.filter(id=connector_id).first()
        if connector:
            session = ChargingSession.objects.create(
                connector=connector,
                id_tag=id_tag_obj,
                start_time=timestamp,
                meter_start=meter_start
            )
            return {"transactionId": session.id, "idTagInfo": {"status": "Accepted"}}
        else:
            return {"error": "InvalidConnectorId"}

    async def handle_status_notification(self, payload):
        connector_id = payload.get("connectorId")
        status = payload.get("status")
        if not all([connector_id, status]):
            return {"error": "MissingRequiredFields"}

        connector = Connector.objects.filter(id=connector_id).first()
        if connector:
            connector.status = status
            connector.save()
            return {}
        else:
            return {"error": "InvalidConnectorId"}

    async def handle_stop_transaction(self, payload):
        transaction_id = payload.get("transactionId")
        meter_stop = payload.get("meterStop")
        timestamp = payload.get("timestamp")

        if not all([transaction_id, meter_stop, timestamp]):
            return {"error": "MissingRequiredFields"}

        session = ChargingSession.objects.filter(id=transaction_id).first()
        if session:
            session.end_time = timestamp
            session.meter_stop = meter_stop
            session.save()
            return {"idTagInfo": {"status": "Accepted"}}
        else:
            return {"error": "InvalidTransactionId"}

