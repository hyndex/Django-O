# ocpp_app/urls.py
from django.urls import path
from .views import (
    change_availability_view,
    change_configuration_view,
    clear_cache_view,
    get_configuration_view,
    remote_start_transaction_view,
    remote_stop_transaction_view,
)

urlpatterns = [
    path('change_availability/', change_availability_view, name='change_availability'),
    path('change_configuration/', change_configuration_view, name='change_configuration'),
    path('clear_cache/', clear_cache_view, name='clear_cache'),
    path('get_configuration/', get_configuration_view, name='get_configuration'),
    path('remote_start_transaction/', remote_start_transaction_view, name='remote_start_transaction'),
    path('remote_stop_transaction/', remote_stop_transaction_view, name='remote_stop_transaction'),
]
