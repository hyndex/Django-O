from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, datetime
from django_otp.oath import TOTP
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import asyncio

import razorpay
import requests
from random import randint

from .models import Device, OTP, Order, PaymentInfo, Plan, PlanUser, UserProfile, Wallet
from .serializers import (
    ChangePasswordSerializer,
    DeviceSerializer,
    OrderSerializer,
    UserSerializer,
    WalletSerializer,
)
from .utils import send_sms

from ocpp_app.remote_start_queue_manager import RemoteStartQueueManager

# Create an instance of RemoteStartQueueManager
remote_start_queue_manager = RemoteStartQueueManager()

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

import logging
from django_otp.oath import TOTP

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
        otp = TOTP(key=device.bin_key, step=device.step, t0=device.t0, digits=device.digits).generate()
        logging.info(f"Generated OTP: {otp}")  # Log the generated OTP

        # Send OTP to user's phone using your SMS gateway
        send_sms(phone, f'Your OTP is: {otp}')

        return Response({'message': 'OTP sent successfully'})
    except Exception as e:
        logging.error(f"Error sending OTP: {e}")
        return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_otp(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    user = User.objects.get(username=phone)
    device = user.totpdevice_set.first()

    if device.verify_token(otp):
        # login(request, user)  # DRF doesn't use Django's login function
        return Response({'message': 'Login successful'})
    else:
        return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_wallet_deposit_order(request):
    user = request.user
    amount = request.data.get('amount')

    # Create a Razorpay order
    razorpay_order = razorpay_client.order.create({
        'amount': int(amount) * 100,  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Create an Order record in the database
    order = Order.objects.create(
        user=user,
        amount=amount,
        gateway_id=razorpay_order['id'],
        gateway_name='Razorpay',
        type='Wallet Deposit',
        status='Pending'
    )

    return Response({
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount
    })

@api_view(['POST'])
def handle_razorpay_payment_success(request):
    user = request.user
    payment_id = request.data.get('razorpay_payment_id')
    razorpay_order_id = request.data.get('razorpay_order_id')
    signature = request.data.get('razorpay_signature')

    # Fetch the order using the Razorpay order ID
    order = Order.objects.get(gateway_id=razorpay_order_id, user=user)

    # Verify the payment signature
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    result = razorpay_client.utility.verify_payment_signature(params_dict)

    if result:
        # Update the order status
        order.status = 'Paid'
        order.save()

        # Update the user's wallet
        wallet, created = Wallet.objects.get_or_create(user=order.user)
        wallet.balance += order.amount
        wallet.save()

        # Save payment info
        PaymentInfo.objects.create(
            order=order,
            user=user,
            amount=order.amount,
            method='Razorpay',
            payment_id=payment_id,  # Add the payment ID here
            captured=True,
            email=request.data.get('email', ''),
            phone=request.data.get('phone', ''),
            currency='INR',
            status='Paid'
        )

        return Response({'message': 'Payment successful'})
    else:
        return Response({'message': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
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
def pay_subscription(request):
    user = request.user
    plan_user_id = request.data.get('plan_user_id')
    plan_user = PlanUser.objects.get(id=plan_user_id, user=user)

    # Create a Razorpay order for the subscription payment
    razorpay_order = razorpay_client.order.create({
        'amount': int(plan_user.plan.price) * 100,  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Create an Order record in the database
    order = Order.objects.create(
        user=user,
        amount=plan_user.plan.price,
        gateway_id=razorpay_order['id'],
        gateway_name='Razorpay',
        type='Subscription',
        status='Pending'
    )

    return Response({
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': plan_user.plan.price
    })

@api_view(['POST'])
def register_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# View for user profile
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# View for deleting user account
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# View for refreshing JWT token
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

# View for setting new password
class SetPasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = User

    def get_object(self, queryset=None):
        return self.request.user

# View for login with password
class LoginWithPasswordView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# View for forgot password
class ForgotPasswordView(APIView):
    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')
        user = User.objects.filter(email=email_or_phone).first() or User.objects.filter(username=email_or_phone).first()

        if user:
            otp = OTP.objects.create(user=user)
            if '@' in email_or_phone:
                send_mail(email_or_phone, otp.code)
            else:
                send_sms(email_or_phone, otp.code)
            return Response({'message': 'OTP sent to your email or phone'}, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# View for verify OTP and set new password
class VerifyOTPView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        new_password = request.data.get('new_password')
        otp = OTP.objects.filter(code=otp_code, is_active=True).first()

        if otp and otp.is_valid():
            user = otp.user
            user.set_password(new_password)
            user.save()
            otp.is_active = False  # Deactivate OTP after use
            otp.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

           


@api_view(['POST'])
def send_otp(request):
    user = request.user
    type = request.data.get('type')

    if type not in ['phone', 'email']:
        return Response({'error': 'Invalid type'}, status=400)

    otp = str(randint(100000, 999999))
    OTP.objects.create(user=user, otp=otp, type=type)

    if type == 'phone':
        phone_number = user.profile.phone_number
        # Send OTP to phone using SMS gateway
        # Example: requests.post('SMS_GATEWAY_URL', data={'phone': phone_number, 'message': f'Your OTP is: {otp}'})
    elif type == 'email':
        email = user.email
        # Send OTP to email
        send_mail(
            'Verify your email',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    return Response({'message': 'OTP sent successfully'})

@api_view(['POST'])
def verify_otp(request):
    user = request.user
    otp = request.data.get('otp')
    type = request.data.get('type')

    if type not in ['phone', 'email']:
        return Response({'error': 'Invalid type'}, status=400)

    otp_object = OTP.objects.filter(user=user, otp=otp, type=type).first()

    if otp_object and otp_object.is_valid():
        if type == 'phone':
            user.profile.is_phone_verified = True
        elif type == 'email':
            user.profile.is_email_verified = True
        user.profile.save()
        otp_object.delete()
        return Response({'message': 'Verification successful'})
    else:
        return Response({'error': 'Invalid or expired OTP'}, status=400)


@api_view(['POST'])
def update_phone(request):
    user = request.user
    new_phone = request.data.get('phone_number')

    if UserProfile.objects.filter(phone_number=new_phone).exists():
        return Response({'error': 'Phone number already exists'}, status=400)

    otp = str(randint(100000, 999999))
    OTP.objects.create(user=user, otp=otp, type='phone')
    # Use the send_sms function to send OTP to the new phone number
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
    # Send OTP to new email
    send_mail(
        'Verify your email',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [new_email],
        fail_silently=False,
    )

    return Response({'message': 'OTP sent to new email'})

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
    else:
        return Response({'error': 'Invalid or expired OTP'}, status=400)




@require_POST
@login_required
def remote_start_charge_with_queue(request):
    cpid = request.POST.get('cpid')
    connector_id = int(request.POST.get('connectorId'))
    id_tag = request.POST.get('idTag')

    if remote_start_queue_manager.is_queue_empty():
        response = asyncio.run(remote_start_queue_manager.start_charging(request.user, cpid, connector_id, id_tag))
        if response.get('status') == 'Accepted':
            return JsonResponse({'message': 'Charging session started'})
        else:
            return JsonResponse({'error': 'Failed to start charging session'}, status=500)
    else:
        position = remote_start_queue_manager.get_user_position(request.user)
        if position == 0:
            asyncio.create_task(remote_start_queue_manager.add_to_queue(request.user, cpid, connector_id, id_tag))
            return JsonResponse({'message': 'Added to remote start queue, you are in position 1'})
        elif position == 1:
            response = asyncio.run(remote_start_queue_manager.start_next_in_queue())
            if response.get('status') == 'Accepted':
                return JsonResponse({'message': 'Charging session started'})
            else:
                return JsonResponse({'error': 'Failed to start charging session'}, status=500)
        else:
            return JsonResponse({'message': f'You are in position {position} in the queue'})