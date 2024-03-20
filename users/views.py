from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Order, Wallet, PaymentInfo, Plan, PlanUser, Device
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Order
from .serializers import WalletSerializer, OrderSerializer
import razorpay
from django.conf import settings

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone')
    user, created = User.objects.get_or_create(username=phone)

    if created:
        device = TOTPDevice(user=user, name='Phone')
        device.save()
    else:
        device = user.totpdevice_set.first()

    otp = TOTP(key=device.bin_key, step=device.step, t0=device.t0, digits=device.digits).generate()
    # Send OTP to user's phone using your SMS gateway
    send_sms(phone, f'Your OTP is: {otp}')

    return Response({'message': 'OTP sent successfully'})

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
        expiry=now() + timezone.timedelta(days=plan.plan_renewal_interval),
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
    user = request.user
    token = request.data.get('token')
    device_type = request.data.get('device_type')

    Device.objects.update_or_create(
        user=user,
        defaults={'token': token, 'device_type': device_type}
    )

    return Response({'message': 'Device registered successfully'})



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
