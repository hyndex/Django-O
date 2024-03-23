# # ocpp_app/urls.py
# from django.urls import path
# from .views_2 import (
#     change_availability_view,
#     change_configuration_view,
#     clear_cache_view,
#     get_configuration_view,
#     remote_start_transaction_view,
#     remote_stop_transaction_view,
# )
# from .views_2 import ChargerViewSet

# router = DefaultRouter()
# router.register(r'chargers', ChargerViewSet, basename='charger')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('change_availability/', change_availability_view, name='change_availability'),
#     path('change_configuration/', change_configuration_view, name='change_configuration'),
#     path('clear_cache/', clear_cache_view, name='clear_cache'),
#     path('get_configuration/', get_configuration_view, name='get_configuration'),
#     path('remote_start_transaction/', remote_start_transaction_view, name='remote_start_transaction'),
#     path('remote_stop_transaction/', remote_stop_transaction_view, name='remote_stop_transaction'),
# ]




# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('remote_start_transaction/', views.remote_start_transaction, name='remote_start_transaction'),
    path('remote_stop_transaction/', views.remote_stop_transaction, name='remote_stop_transaction'),
    path('get_configuration/', views.get_configuration, name='get_configuration'),
    path('set_configuration/', views.set_configuration, name='set_configuration'),
    path('clear_cache/', views.clear_cache, name='clear_cache'),
    path('reset_charger/', views.reset_charger, name='reset_charger'),
]
