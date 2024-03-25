from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'chargers', views.ChargerViewSet, basename='charger')

urlpatterns = [
    path('', include(router.urls)),
    path('remote_start_transaction/', views.RemoteStartTransactionView.as_view(), name='remote_start_transaction'),
    path('remote_stop_transaction/', views.RemoteStopTransactionView.as_view(), name='remote_stop_transaction'),
    path('get_configuration/', views.GetConfigurationView.as_view(), name='get_configuration'),
    path('set_configuration/', views.SetConfigurationView.as_view(), name='set_configuration'),
    path('clear_cache/', views.ClearCacheView.as_view(), name='clear_cache'),
    path('reset_charger/', views.ResetChargerView.as_view(), name='reset_charger'),
    path('change-availability/', views.ChangeAvailabilityView.as_view(), name='change-availability'),
    path('trigger-message/', views.TriggerMessageView.as_view(), name='trigger-message'),
    path('update-firmware/', views.UpdateFirmwareView.as_view(), name='update-firmware'),
    path('get-local-list-version/', views.GetLocalListVersionView.as_view(), name='get-local-list-version'),
    path('send-local-list/', views.SendLocalListView.as_view(), name='send-local-list'),

]
