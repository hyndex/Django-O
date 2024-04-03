from datetime import datetime, timedelta
from django.db.models import Q
from ocpp_app.models import ChargingSession, MeterValues
from django.conf import settings
from django.db import transaction

def check_for_meter_value_timeout():
    try:
        timeout_seconds = getattr(settings, 'METER_VALUE_TIMEOUT', 300)  # Default to 5 minutes if not set
        timeout_time = datetime.now() - timedelta(seconds=timeout_seconds)

        # Find active sessions that have not received a meter value update within the timeout period
        sessions = ChargingSession.objects.filter(
            meter_stop__isnull=True,
            end_time__isnull=True,
            start_time__lte=timeout_time
        )

        for session in sessions:
            try:
                # Find the latest meter value for the session
                meter_value = MeterValues.objects.filter(
                    charging_session=session,
                    unit__in=['kWh', 'Wh']
                ).order_by('-timestamp').first()

                if not meter_value:
                    # If no meter value is found, create a default one
                    meter_value = MeterValues(
                        charging_session=session,
                        measurand='Energy.Active.Export.Interval',
                        unit='Wh',
                        value=0
                    )

                if meter_value.measurand.lower() in ['energy.active.export.register', 'energy.active.import.register']:
                    meter_value.measurand = 'Energy.Active.Export.Interval'
                    meter_value.value -= session.meter_start / 1000

                meter_value.value = float(meter_value.value)
                if meter_value.unit.lower() == 'wh':
                    meter_value.unit = 'kWh'
                    meter_value.value /= 1000

                meter_end = session.meter_start + meter_value.value * 1000  # Convert kWh to Wh

                # Update the session with the calculated meter stop value and reason for timeout
                session.meter_stop = meter_end
                session.end_time = datetime.now()
                session.reason = 'Timeout'
                session.save()

            except Exception as inner_error:
                print(f'Error processing session {session.id}:', inner_error)

    except Exception as error:
        print('Error checking for meter value timeouts:', error)


