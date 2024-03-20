from rest_framework import serializers
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
        fields = ['id', 'user', 'amount', 'tax', 'gateway_id', 'gateway_name', 'order_serial', 'type', 'limit_type', 'property', 'status', 'payment_info', 'session_billing', 'wallet']
        read_only_fields = ['user']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'registration_id', 'device_type']