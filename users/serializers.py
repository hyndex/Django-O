from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Wallet, Order, PaymentInfo, SessionBilling, Device
from django.contrib.auth.models import User
from rest_framework import serializers
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import UserProfile, OTP

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



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Create a TOTP device for the user
        TOTPDevice.objects.create(user=user, name='default')
        return user

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context['request'].user
        device = user.totpdevice_set.first()
        if not device.verify_token(data['otp']):
            raise serializers.ValidationError('Invalid OTP')
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'email', 'city', 'state', 'pin', 'address']
        extra_kwargs = {'email': {'required': False}}

    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exclude(user=self.context['request'].user).exists():
            raise serializers.ValidationError('Phone number already in use')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.context['request'].user.id).exists():
            raise serializers.ValidationError('Email already in use')
        return value



from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError('User with this phone number does not exist')
        return value


class VerifyOTPAndSetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField()

    def validate(self, data):
        user_profile = self.context['user_profile']
        otp_object = OTP.objects.filter(user=user_profile.user, otp=data['otp'], type='phone').first()

        if not otp_object or not otp_object.is_valid():
            raise serializers.ValidationError('Invalid or expired OTP')

        return data

    def save(self, **kwargs):
        user = self.context['user_profile'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        # Deactivate the OTP after use
        otp_object = OTP.objects.get(user=user, otp=self.validated_data['otp'], type='phone')
        otp_object.is_active = False
        otp_object.save()
