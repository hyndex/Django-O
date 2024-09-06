from django.http import JsonResponse
from rest_framework import generics, status
from .models import PowerPlant, EnergyGenerationLog
from .serializers import PowerPlantSerializer, EnergyGenerationLogSerializer
from rest_framework.permissions import IsAuthenticated

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

# Export Energy Generation Logs
def export_logs(request, plant_id):
    logs = EnergyGenerationLog.objects.filter(power_plant_id=plant_id)
    data = [{"timestamp": log.timestamp, "energy_generated": log.energy_generated_mwh} for log in logs]
    return JsonResponse(data, safe=False)
