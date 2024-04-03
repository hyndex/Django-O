from django.db.models import Q
from ocpp_app.models import MeterValues, ChargingSession
import datetime

def meter_value_check_stop_transaction(charging_session_id):
    try:
        meter_values = MeterValues.objects.filter(
            charging_session_id=charging_session_id,
            unit__in=['Wh', 'kWh']
        ).select_related('charging_session')

        stop = False

        if meter_values.exists():
            charging_session = meter_values[0].charging_session

            for meter_value in meter_values:
                value_in_wh = float(meter_value.value)

                # Convert kWh to Wh if necessary
                if meter_value.unit.lower() == 'kwh':
                    value_in_wh *= 1000

                if charging_session.limit_type.upper() == 'KWH' and (
                    meter_value.measurand.lower() in [
                        'energy.active.export.register',
                        'energy.active.import.register',
                        'energy.active.export.interval',
                        'energy.active.import.interval'
                    ] and value_in_wh - charging_session.meter_start >= charging_session.limit * 1000
                ):
                    stop = True

            # Check for stopping condition based on time
            if charging_session.limit_type.upper() == 'TIME':
                start_time = charging_session.start_time
                current_time = datetime.datetime.now()
                elapsed_time_in_minutes = (current_time - start_time).total_seconds() / 60

                if elapsed_time_in_minutes >= charging_session.limit:
                    stop = True

        return stop

    except Exception as error:
        print(error)
        return False
