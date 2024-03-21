from rest_framework import serializers
from .models import (BankAccount, Settlement, SettlementRequest,
                     PartnerCommissionGroup, PartnerCommission, PartnerCommissionGroupUser,
                     PartnerEmployeeList, UserPartnerEmployeeList, CommissionPayment)


class BankAccountSerializer(serializers.ModelSerializer):
    owner = ChargerOwnerSerializer(read_only=True)

    class Meta:
        model = BankAccount
        fields = '__all__'

class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = '__all__'

class SettlementRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettlementRequest
        fields = '__all__'

class PartnerCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerCommission
        fields = '__all__'

class PartnerCommissionGroupSerializer(serializers.ModelSerializer):
    commissions = PartnerCommissionSerializer(many=True, read_only=True)

    class Meta:
        model = PartnerCommissionGroup
        fields = '__all__'

class PartnerCommissionGroupUserSerializer(serializers.ModelSerializer):
    partner_commission_group = PartnerCommissionGroupSerializer(read_only=True)

    class Meta:
        model = PartnerCommissionGroupUser
        fields = '__all__'

class PartnerEmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerEmployeeList
        fields = '__all__'

class UserPartnerEmployeeListSerializer(serializers.ModelSerializer):
    host_custom_user_list = PartnerEmployeeListSerializer(read_only=True)

    class Meta:
        model = UserPartnerEmployeeList
        fields = '__all__'



class CommissionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionPayment
        fields = '__all__'
