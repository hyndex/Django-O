# battery_storage/urls.py
from django.urls import path
from .views import BatteryStorageViewSet, BatteryUsageLogCreateView, export_logs

urlpatterns = [
    path('battery-storages/', BatteryStorageViewSet.as_view(), name='battery_storages'),
    path('battery-log/', BatteryUsageLogCreateView.as_view(), name='battery_log'),
    path('export-logs/<int:storage_id>/', export_logs, name='export_logs'),
]