# power_plant/urls.py
from django.urls import path
from .views import PowerPlantViewSet, EnergyGenerationLogCreateView, export_logs

urlpatterns = [
    path('power-plants/', PowerPlantViewSet.as_view(), name='power_plants'),
    path('energy-log/', EnergyGenerationLogCreateView.as_view(), name='energy_log'),
    path('export-logs/<int:plant_id>/', export_logs, name='export_logs'),
]