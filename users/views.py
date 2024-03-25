# Standard library imports
from datetime import timedelta, datetime
from random import randint

# Django imports
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password

# Third-party imports
import razorpay
import requests
from rest_framework import status, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Local imports from your application
from .models import Device, OTP, Order, PaymentInfo, Plan, PlanUser, UserProfile, Wallet
from .serializers import (
    DeviceSerializer,
    ForgotPasswordSerializer,
    OrderSerializer,
    OTPVerificationSerializer,
    SetPasswordSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    VerifyOTPAndSetPasswordSerializer,
    WalletSerializer,
)
from .utils import send_otp_email, send_otp_sms, send_sms

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


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

class UserRegistrationView(views.APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginWithOTPView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            login(request, request.user)
            refresh = RefreshToken.for_user(request.user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(views.APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_password = request.data.get('new_password')
        if new_password:
            request.user.password = make_password(new_password)
            request.user.save()
            return Response({'message': 'Password set successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class SetPasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def request_otp(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user_profile = UserProfile.objects.get(phone_number=phone_number)
            otp = str(randint(100000, 999999))
            OTP.objects.create(user=user_profile.user, otp=otp, type='phone')
            send_otp_sms(phone_number, otp)
            return Response({'message': 'OTP sent to your phone'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_otp_and_set_password(self, request):
        user_profile = UserProfile.objects.get(phone_number=request.data.get('phone_number'))
        serializer = VerifyOTPAndSetPasswordSerializer(data=request.data, context={'user_profile': user_profile})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
