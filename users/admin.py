from django.contrib import admin
from .models import (
    UserProfile, PaymentInfo, SessionBilling, Plan, PlanUser, Promotion, Device, TaxTemplate, Wallet, Order, OTP
)
from unfold.admin import ModelAdmin, TabularInline
from django.contrib import admin

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'state', 'is_phone_verified', 'is_email_verified']
    search_fields = ['user__username', 'phone_number', 'city', 'state']
    list_filter = ['is_phone_verified', 'is_email_verified', 'city', 'state']


class PaymentInfoInline(TabularInline):
    model = PaymentInfo
    extra = 1


class SessionBillingInline(TabularInline):
    model = SessionBilling
    extra = 1


class WalletInline(TabularInline):
    model = Wallet
    extra = 1


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'user', 'amount', 'tax', 'type', 'status']
    inlines = [PaymentInfoInline, SessionBillingInline, WalletInline]
    search_fields = ['user__username', 'type', 'status']
    list_filter = ['type', 'status']


@admin.register(PaymentInfo)
class PaymentInfoAdmin(ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'captured', 'refund', 'status']
    search_fields = ['order__id', 'method', 'status']
    list_filter = ['method', 'captured', 'status']


@admin.register(SessionBilling)
class SessionBillingAdmin(ModelAdmin):
    list_display = ['id', 'session', 'amount_added', 'amount_consumed', 'amount_refunded']
    search_fields = ['session__id']
    # Assuming session model is registered similarly


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ['id', 'is_corporate', 'corporate_name', 'percent_discount_enable', 'is_active', 'type']
    search_fields = ['corporate_name', 'type']
    list_filter = ['is_corporate', 'percent_discount_enable', 'is_active', 'type']


@admin.register(PlanUser)
class PlanUserAdmin(ModelAdmin):
    list_display = ['id', 'user', 'plan', 'expiry', 'active']
    search_fields = ['user__username', 'plan__id']
    list_filter = ['active']


@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    list_display = ['id', 'name', 'type', 'start_time', 'end_time', 'is_active']
    search_fields = ['name', 'type']
    list_filter = ['is_active', 'type']


@admin.register(Device)
class DeviceAdmin(ModelAdmin):
    list_display = ['user', 'device_id', 'device_type']
    search_fields = ['user__username', 'device_id']
    list_filter = ['device_type']


@admin.register(TaxTemplate)
class TaxTemplateAdmin(ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display = ['user', 'amount', 'start_balance', 'end_balance', 'reason']
    search_fields = ['user__username', 'reason']
    list_filter = ['reason']


@admin.register(OTP)
class OTPAdmin(ModelAdmin):
    list_display = ['user', 'otp', 'created_at', 'type']
    search_fields = ['user__username', 'otp']
    list_filter = ['type']


# Optional: Automatically create or update UserProfile on User creation/update
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
    instance.profile.save()
