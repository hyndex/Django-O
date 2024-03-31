from django.http import JsonResponse
from .models import OEMCharger, IPLog
from .utils import verify_signature
import base64

def log_ip(request):
    unique_id = request.POST.get('unique_id')
    ip_address = request.POST.get('ip_address')
    firmware_version = request.POST.get('firmware_version')
    signature = base64.b64decode(request.POST.get('signature', ''))

    try:
        charger = OEMCharger.objects.get(unique_id=unique_id)
    except OEMCharger.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Charger not found'}, status=404)

    data = f"{ip_address}|{firmware_version}"
    if verify_signature(charger.public_key, data, signature):
        IPLog.objects.create(charger=charger, ip_address=ip_address, firmware_version=firmware_version)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
