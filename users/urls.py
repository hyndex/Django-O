from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('send_otp/', send_otp, name='send_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('create_wallet_deposit_order/', create_wallet_deposit_order, name='create_wallet_deposit_order'),
    path('razorpay_payment_success/', handle_razorpay_payment_success, name='razorpay_payment_success'),
    path('subscribe_to_plan/', subscribe_to_plan, name='subscribe_to_plan'),
    path('pay_subscription/', pay_subscription, name='pay_subscription'),
    path('register_device/', register_device, name='register_device'),
] + router.urls
