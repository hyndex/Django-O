from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'forgot_password', views.ForgotPasswordViewSet, basename='forgot_password')

urlpatterns = [
    path('create_wallet_deposit_order/', views.create_wallet_deposit_order, name='create_wallet_deposit_order'),
    path('handle_razorpay_payment_success/', views.handle_razorpay_payment_success, name='handle_razorpay_payment_success'),
    path('subscribe_to_plan/', views.subscribe_to_plan, name='subscribe_to_plan'),
    path('pay_subscription/', views.pay_subscription, name='pay_subscription'),
    path('register_device/', views.register_device, name='register_device'),
    path('user_profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('delete_account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('refresh_token/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('set_password/', views.SetPasswordView.as_view(), name='set_password'),
    path('login_with_otp/', views.LoginWithOTPView.as_view(), name='login_with_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('', include(router.urls)),
]
