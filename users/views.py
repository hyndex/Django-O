from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.oath import TOTP
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import timedelta, datetime
from .serializers import UserSerializer, ChangePasswordSerializer, DeviceSerializer, OrderSerializer, WalletSerializer
from .models import Device, OTP, Order, PaymentInfo, Plan, PlanUser, UserProfile, Wallet
from payments import get_payment_model
from .utils import send_sms
from ocpp_app.queue_manager import RemoteStartQueueManager
from random import randint
import logging
from rest_framework.permissions import IsAuthenticated

# Create an instance of RemoteStartQueueManager
remote_start_queue_manager = RemoteStartQueueManager()

# Payments model
Payment = get_payment_model()

# Helper function for creating a payment using tenant-specific payment settings
def create_payment(tenant, amount, description, payment_method, user_email):
    # Get tenant-specific payment variants
    payment_variants = settings.get_payment_variants(tenant)

    # Check if the specified payment method exists for the tenant
    if payment_method not in payment_variants:
        raise ValueError(f"Payment method {payment_method} not available for this tenant.")

    # Set the default currency or use tenant's currency
    currency = tenant.currency

    # Create the payment object using the tenant's payment variant
    payment = Payment.objects.create(
        variant=payment_method,
        description=description,
        total=amount,
        currency=currency,
        billing_email=user_email,
    )
    return payment.get_process_url()

# OTP functionality
@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone')
    user, created = User.objects.get_or_create(username=phone)

    if created:
        device = TOTPDevice(user=user, name='Phone')
        device.save()
    else:
        device = user.totpdevice_set.first()

    try:
        otp = TOTP(key=device.bin_key, step=device.step, t0=device.t0, digits=device.digits).token()
        logging.info(f"Generated OTP: {otp}")
        send_sms(phone, f'Your OTP is: {otp}')
        return Response({'message': 'OTP sent successfully'})
    except Exception as e:
        logging.error(f"Error sending OTP: {e}")
        return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def verify_otp(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    user = User.objects.filter(username=phone).first()

    if user:
        device = user.totpdevice_set.first()
        if device and device.verify_token(otp):
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            user.profile.is_phone_verified = True
            user.profile.save()
            user_data = UserSerializer(user).data
            return Response({
                'refresh_token': str(refresh),
                'access_token': str(access_token),
                'user': user_data,
                'message': 'Login successful'
            })
        return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Payment functionality
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_wallet_deposit_order(request):
    user = request.user
    amount = request.data.get('amount')
    tenant = request.tenant

    # Create payment using tenant's preferred gateway
    payment_url = create_payment(tenant, amount, "Wallet Deposit", "razorpay", user.email)

    # Create an Order record in the database
    order = Order.objects.create(
        user=user,
        amount=amount,
        gateway_id=payment_url,  # Save the payment process URL
        gateway_name='Razorpay',
        type='Wallet Deposit',
        status='Pending'
    )

    return Response({
        'payment_url': payment_url,
        'amount': amount
    })

@api_view(['POST'])
def handle_payment_success(request):
    user = request.user
    payment_id = request.data.get('payment_id')
    gateway_name = request.data.get('gateway_name')

    # Fetch the order using the gateway name and payment ID
    order = Order.objects.filter(gateway_id=payment_id, user=user).first()

    if order:
        # Update the order status
        order.status = 'Paid'
        order.save()

        # Update user's wallet
        wallet, created = Wallet.objects.get_or_create(user=order.user)
        wallet.balance += order.amount
        wallet.save()

        # Save payment info
        PaymentInfo.objects.create(
            order=order,
            user=user,
            amount=order.amount,
            method=gateway_name,
            payment_id=payment_id,
            captured=True,
            email=request.data.get('email', ''),
            phone=request.data.get('phone', ''),
            currency='INR',
            status='Paid'
        )
        return Response({'message': 'Payment successful'})
    return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# Plan subscription
@api_view(['POST'])
@login_required
def subscribe_to_plan(request):
    user = request.user
    plan_id = request.data.get('plan_id')
    plan = Plan.objects.get(id=plan_id)

    # Create a PlanUser instance
    PlanUser.objects.create(
        user=user,
        plan=plan,
        expiry=datetime.now() + timedelta(days=plan.plan_renewal_interval),
        validity=plan.plan_renewal_interval
    )
    return Response({'message': 'Subscribed to plan successfully'})

@api_view(['POST'])
@login_required
def pay_subscription(request):
    user = request.user
    plan_user_id = request.data.get('plan_user_id')
    plan_user = PlanUser.objects.get(id=plan_user_id, user=user)
    tenant = request.tenant

    # Create payment using tenant's preferred gateway
    payment_url = create_payment(tenant, plan_user.plan.price, "Subscription", "razorpay", user.email)

    # Create an Order record in the database
    order = Order.objects.create(
        user=user,
        amount=plan_user.plan.price,
        gateway_id=payment_url,
        gateway_name='Razorpay',
        type='Subscription',
        status='Pending'
    )

    return Response({
        'payment_url': payment_url,
        'amount': plan_user.plan.price
    })

# Device registration
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Wallet and Order viewsets
class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# User profile management
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# Account deletion
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# JWT token management
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                return Response({'access': str(token.access_token)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)

# Password management
class SetPasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if self.object.has_usable_password() and not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login functionality
class LoginWithPasswordView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            user_data = UserSerializer(user).data
            return Response({
                'refresh_token': str(refresh),
                'access_token': str(access_token),
                'user': user_data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Forgot password functionality
class ForgotPasswordView(APIView):
    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')
        user = User.objects.filter(email=email_or_phone).first() or User.objects.filter(username=email_or_phone).first()

        if user:
            code = str(randint(100000, 999999))
            otp = OTP.objects.create(user=user, otp=code)
            if '@' in email_or_phone:
                send_mail(email_or_phone, otp.otp)
            else:
                send_sms(email_or_phone, otp.otp)
            return Response({'message': 'OTP sent to your email or phone'}, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Verify OTP for password reset
class VerifyOTPView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        new_password = request.data.get('new_password')
        otp = OTP.objects.filter(otp=otp_code, is_active=True).first()

        if otp and otp.is_valid():
            user = otp.user
            user.set_password(new_password)
            user.save()
            otp.is_active = False
            otp.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

# Phone and email updates
@api_view(['POST'])
def update_phone(request):
    user = request.user
    new_phone = request.data.get('phone_number')

    if UserProfile.objects.filter(phone_number=new_phone).exists():
        return Response({'error': 'Phone number already exists'}, status=400)

    otp = str(randint(100000, 999999))
    OTP.objects.create(user=user, otp=otp, type='phone')
    send_sms(new_phone, f'Your OTP is: {otp}')
    return Response({'message': 'OTP sent to new phone number'})

@api_view(['POST'])
def update_email(request):
    user = request.user
    new_email = request.data.get('email')

    if User.objects.filter(email=new_email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    otp = str(randint(100000, 999999))
    OTP.objects.create(user=user, otp=otp, type='email')
    send_mail(
        'Verify your email',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [new_email],
        fail_silently=False,
    )
    return Response({'message': 'OTP sent to new email'})

# OTP verification for updates
@api_view(['POST'])
def verify_update(request):
    user = request.user
    otp = request.data.get('otp')
    type = request.data.get('type')
    new_value = request.data.get('new_value')

    otp_object = OTP.objects.filter(user=user, otp=otp, type=type).first()

    if otp_object and otp_object.is_valid():
        if type == 'phone':
            user.profile.phone_number = new_value
            user.profile.is_phone_verified = True
        elif type == 'email':
            user.email = new_value
            user.profile.is_email_verified = True
        user.save()
        user.profile.save()
        otp_object.delete()
        return Response({'message': 'Update successful'})
    return Response({'error': 'Invalid or expired OTP'}, status=400)

# Remote charging session management
@require_POST
@login_required
async def remote_start_charge_with_queue(request):
    cpid = request.POST.get('cpid')
    connector_id = int(request.POST.get('connectorId'))
    id_tag = request.POST.get('idTag')

    await remote_start_queue_manager.add_to_queue(request.user, cpid, connector_id, id_tag)
    response = await remote_start_queue_manager.start_next_in_queue()

    if response.get('status') == 'Accepted':
        return JsonResponse({'message': 'Charging session started'})
    elif response.get('error'):
        return JsonResponse({'error': response.get('error')}, status=500)
    return JsonResponse({'message': 'Added to remote start queue'})
