from celery import shared_task
from .utils.check_metervalue_timeout import check_for_meter_value_timeout
from .utils.metervalue_check_stop_transaction import meter_value_check_stop_transaction

@shared_task
def task_check_for_meter_value_timeout():
    check_for_meter_value_timeout()

@shared_task
def task_meter_value_check_stop_transaction(charging_session_id):
    return meter_value_check_stop_transaction(charging_session_id)
