from django.contrib import admin
from .models import (
    PartnerCommissionMemberGroup, PartnerCommissionMember, ChargerCommission,
    BankAccount, SettlementRequest, Settlement, PartnerEmployeeList, UserPartnerEmployeeList,
    PartnerCommissionMemberGroupPlan, PlanPartnerEmployeeList, CommissionPayment
)

# Utility classes for inline model admin
class PartnerCommissionMemberInline(admin.TabularInline):
    model = PartnerCommissionMember
    extra = 1

class ChargerCommissionInline(admin.TabularInline):
    model = ChargerCommission
    extra = 1

class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 1

class SettlementRequestInline(admin.TabularInline):
    model = SettlementRequest
    extra = 1

class SettlementInline(admin.TabularInline):
    model = Settlement
    extra = 1

class UserPartnerEmployeeListInline(admin.TabularInline):
    model = UserPartnerEmployeeList
    extra = 1

class PlanPartnerEmployeeListInline(admin.TabularInline):
    model = PlanPartnerEmployeeList
    extra = 1

class CommissionPaymentInline(admin.TabularInline):
    model = CommissionPayment
    extra = 1

# Model Admins
@admin.register(PartnerCommissionMemberGroup)
class PartnerCommissionMemberGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'host_type', 'enable_user_wise_bank_settlement', 'created_at', 'updated_at']
    inlines = [PartnerCommissionMemberInline, ChargerCommissionInline]
    search_fields = ['name', 'host_type']
    list_filter = ['host_type', 'enable_user_wise_bank_settlement']

@admin.register(PartnerCommissionMember)
class PartnerCommissionMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'commission', 'commission_type', 'status', 'created_at', 'updated_at']
    inlines = [BankAccountInline, CommissionPaymentInline]
    search_fields = ['user__username', 'commission_type', 'status']
    list_filter = ['commission_type', 'status']

@admin.register(ChargerCommission)
class ChargerCommissionAdmin(admin.ModelAdmin):
    list_display = ['commission', 'commission_type', 'status', 'user', 'created_at', 'updated_at']
    search_fields = ['commission_type', 'status', 'user__username']
    list_filter = ['commission_type', 'status']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['partner_commission_member', 'account_number', 'verified', 'active']
    search_fields = ['account_number', 'partner_commission_member__user__username']
    list_filter = ['verified', 'active']

@admin.register(SettlementRequest)
class SettlementRequestAdmin(admin.ModelAdmin):
    list_display = ['amount', 'status', 'note']
    search_fields = ['status']
    list_filter = ['status']

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ['settlement_request', 'amount', 'reason', 'note']
    search_fields = ['reason']
    inlines = [SettlementRequestInline]

@admin.register(PartnerEmployeeList)
class PartnerEmployeeListAdmin(admin.ModelAdmin):
    list_display = ['name', 'list_type', 'created_at', 'updated_at']
    inlines = [UserPartnerEmployeeListInline]
    search_fields = ['name', 'list_type']
    list_filter = ['list_type']

@admin.register(UserPartnerEmployeeList)
class UserPartnerEmployeeListAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_blocked', 'expiry_date']
    search_fields = ['user__username', 'is_blocked']
    list_filter = ['is_blocked']

@admin.register(PartnerCommissionMemberGroupPlan)
class PartnerCommissionMemberGroupPlanAdmin(admin.ModelAdmin):
    list_display = ['percent_discount_enable', 'price', 'monthly_kwh_limit', 'is_active', 'type']
    search_fields = ['type']
    list_filter = ['is_active', 'type']

@admin.register(PlanPartnerEmployeeList)
class PlanPartnerEmployeeListAdmin(admin.ModelAdmin):
    list_display = ['partner_employee_list', 'plan', 'expiry', 'active', 'date_created']
    search_fields = ['partner_employee_list__name', 'plan__type']
    list_filter = ['active']

@admin.register(CommissionPayment)
class CommissionPaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'status', 'created_at', 'updated_at']
    search_fields = ['status']
    list_filter = ['status']

