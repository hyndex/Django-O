import boto3
from django.core.mail import send_mail

def send_sms(phone_number, message):
    client = boto3.client('sns')
    response = client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
    return response



def send_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'your-email@example.com',  # Your verified SES email
        recipient_list
    )

