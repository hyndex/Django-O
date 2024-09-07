from django.http import JsonResponse
from rest_framework import generics, status
from .models import PowerPlant, EnergyGenerationLog
from .serializers import PowerPlantSerializer, EnergyGenerationLogSerializer
from rest_framework.permissions import IsAuthenticated
# Export Energy Generation Logs
import csv
import json
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .models import EnergyGenerationLog, PowerPlant
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime


# List and Create Power Plants
class PowerPlantViewSet(generics.ListCreateAPIView):
    queryset = PowerPlant.objects.all()
    serializer_class = PowerPlantSerializer
    permission_classes = [IsAuthenticated]

# Create Energy Generation Log (real-time logging)
class EnergyGenerationLogCreateView(generics.CreateAPIView):
    serializer_class = EnergyGenerationLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_energy_logs_csv(request, plant_id):
    """
    Export Energy Generation Logs to CSV format.
    """
    try:
        plant = PowerPlant.objects.get(id=plant_id)
        logs = EnergyGenerationLog.objects.filter(power_plant=plant).order_by('-timestamp')

        # Apply pagination
        paginator = Paginator(logs, 5000)  # Fetch in chunks of 5000 rows at a time for large datasets
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="energy_logs_{plant_id}_{datetime.now().strftime("%Y-%m-%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Energy Generated (MWh)', 'Exported to Grid (MWh)', 'Transmission Loss (MWh)'])

        for log in page_obj:
            writer.writerow([log.timestamp, log.energy_generated_mwh, log.grid_exported_mwh, log.grid_loss_mwh])

        return response

    except PowerPlant.DoesNotExist:
        return JsonResponse({"error": "Power Plant not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_energy_logs_json(request, plant_id):
    """
    Export Energy Generation Logs to JSON format.
    """
    try:
        plant = PowerPlant.objects.get(id=plant_id)
        logs = EnergyGenerationLog.objects.filter(power_plant=plant).order_by('-timestamp')

        # Apply pagination
        paginator = Paginator(logs, 5000)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        log_data = []
        for log in page_obj:
            log_data.append({
                'timestamp': log.timestamp.isoformat(),
                'energy_generated_mwh': float(log.energy_generated_mwh),
                'grid_exported_mwh': float(log.grid_exported_mwh),
                'grid_loss_mwh': float(log.grid_loss_mwh)
            })

        return JsonResponse(log_data, safe=False)

    except PowerPlant.DoesNotExist:
        return JsonResponse({"error": "Power Plant not found"}, status=404)

