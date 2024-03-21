from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Wallet, Order, PaymentInfo, SessionBilling, Device

class PaymentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentInfo
        fields = '__all__'

class SessionBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionBilling
        fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    payment_info = PaymentInfoSerializer(read_only=True)
    session_billing = SessionBillingSerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'amount', 'tax', 'gateway_id', 'gateway_name', 'order_serial', 'type', 'limit_type', 'property', 'status', 'payment_info', 'session_billing', 'wallet']
        read_only_fields = ['user']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'registration_id', 'device_type']



class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='profile.phone_number')
    city = serializers.CharField(source='profile.city')
    state = serializers.CharField(source='profile.state')
    pin = serializers.CharField(source='profile.pin')
    address = serializers.CharField(source='profile.address')
    is_phone_verified = serializers.BooleanField(source='profile.is_phone_verified')
    is_email_verified = serializers.BooleanField(source='profile.is_email_verified')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            'city', 'state', 'pin', 'address', 'is_phone_verified', 'is_email_verified'
        ]
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'phone_number': {'required': True}
        }

    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value