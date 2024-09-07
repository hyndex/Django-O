from django.http import JsonResponse
from rest_framework import generics, status
from .models import BatteryStorage, BatteryUsageLog
from .serializers import BatteryStorageSerializer, BatteryUsageLogSerializer
from rest_framework.permissions import IsAuthenticated
import csv
import json
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .models import EnergyGenerationLog, PowerPlant
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

# List and Create Battery Storage Systems
class BatteryStorageViewSet(generics.ListCreateAPIView):
    queryset = BatteryStorage.objects.all()
    serializer_class = BatteryStorageSerializer
    permission_classes = [IsAuthenticated]

# Create Battery Usage Log (real-time logging)
class BatteryUsageLogCreateView(generics.CreateAPIView):
    serializer_class = BatteryUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Export Battery Usage Logs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_battery_usage_logs_csv(request, battery_id):
    """
    Export Battery Usage Logs to CSV format.
    """
    try:
        battery = BatteryStorage.objects.get(id=battery_id)
        logs = BatteryUsageLog.objects.filter(battery_storage=battery).order_by('-timestamp')

        # Apply pagination for large datasets
        paginator = Paginator(logs, 5000)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="battery_usage_logs_{battery_id}_{datetime.now().strftime("%Y-%m-%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Energy Input (MWh)', 'Energy Output (MWh)', 'Efficiency Loss (MWh)', 'State of Charge (%)'])

        for log in page_obj:
            writer.writerow([log.timestamp, log.energy_input_mwh, log.energy_output_mwh, log.efficiency_loss_mwh, log.state_of_charge])

        return response

    except BatteryStorage.DoesNotExist:
        return JsonResponse({"error": "Battery Storage not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_battery_usage_logs_json(request, battery_id):
    """
    Export Battery Usage Logs to JSON format.
    """
    try:
        battery = BatteryStorage.objects.get(id=battery_id)
        logs = BatteryUsageLog.objects.filter(battery_storage=battery).order_by('-timestamp')

        # Apply pagination for large datasets
        paginator = Paginator(logs, 5000)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        log_data = []
        for log in page_obj:
            log_data.append({
                'timestamp': log.timestamp.isoformat(),
                'energy_input_mwh': float(log.energy_input_mwh) if log.energy_input_mwh else None,
                'energy_output_mwh': float(log.energy_output_mwh) if log.energy_output_mwh else None,
                'efficiency_loss_mwh': float(log.efficiency_loss_mwh),
                'state_of_charge': float(log.state_of_charge)
            })

        return JsonResponse(log_data, safe=False)

    except BatteryStorage.DoesNotExist:
        return JsonResponse({"error": "Battery Storage not found"}, status=404)

