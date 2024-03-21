from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('create_wallet_deposit_order/', views.create_wallet_deposit_order, name='create_wallet_deposit_order'),
    path('handle_razorpay_payment_success/', views.handle_razorpay_payment_success, name='handle_razorpay_payment_success'),
    path('subscribe_to_plan/', views.subscribe_to_plan, name='subscribe_to_plan'),
    path('pay_subscription/', views.pay_subscription, name='pay_subscription'),
    path('register_device/', views.register_device, name='register_device'),
    path('user_profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('delete_account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('refresh_token/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('set_password/', views.SetPasswordView.as_view(), name='set_password'),
    path('login_with_password/', views.LoginWithPasswordView.as_view(), name='login_with_password'),
    path('forgot_password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify_otp_update/', views.VerifyOTPView.as_view(), name='verify_otp_update'),
    path('update_phone/', views.update_phone, name='update_phone'),
    path('update_email/', views.update_email, name='update_email'),
    path('verify_update/', views.verify_update, name='verify_update'),
]

urlpatterns += router.urls
