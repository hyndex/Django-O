import boto3
from django.core.mail import send_mail
from push_notifications.models import APNSDevice, GCMDevice
from botocore.exceptions import BotoCoreError, ClientError

def send_sms(phone_number, message):
    client = boto3.client('sns', region_name='ap-south-1')
    try:
        response = client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        return response
    except (BotoCoreError, ClientError) as e:
        # You can add logging or other error handling here
        return {"error": str(e)}



def send_push_notification(user, message):
    devices = APNSDevice.objects.filter(user=user)
    devices.send_message(message)

    devices = GCMDevice.objects.filter(user=user)
    devices.send_message(message)
