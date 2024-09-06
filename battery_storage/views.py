from django.http import JsonResponse
from rest_framework import generics, status
from .models import BatteryStorage, BatteryUsageLog
from .serializers import BatteryStorageSerializer, BatteryUsageLogSerializer
from rest_framework.permissions import IsAuthenticated

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
def export_logs(request, storage_id):
    logs = BatteryUsageLog.objects.filter(battery_storage_id=storage_id)
    data = [{"timestamp": log.timestamp, "energy_input": log.energy_input_mwh, "energy_output": log.energy_output_mwh, "status": log.status} for log in logs]
    return JsonResponse(data, safe=False)
