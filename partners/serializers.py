from rest_framework import serializers
from .models import (
    PartnerCommissionMemberGroup,
    PartnerCommissionMember,
    BankAccount,
    Settlement,
    SettlementRequest,
    PartnerEmployeeList,
    UserPartnerEmployeeList,
    CommissionPayment
)
from users.models import SessionBilling
from ocpp_app.models import ChargingSession
class BankAccountSerializer(serializers.ModelSerializer):
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

class CommissionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionPayment
        fields = '__all__'

class PartnerCommissionMemberSerializer(serializers.ModelSerializer):
    bank_accounts = BankAccountSerializer(many=True, read_only=True)
    commission_payments = CommissionPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = PartnerCommissionMember
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

class PartnerCommissionMemberGroupSerializer(serializers.ModelSerializer):
    commission_members = PartnerCommissionMemberSerializer(many=True, read_only=True)

    class Meta:
        model = PartnerCommissionMemberGroup
        fields = '__all__'


class SessionBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionBilling
        fields = '__all__'

class ChargingSessionSerializer(serializers.ModelSerializer):
    session_billing = SessionBillingSerializer(read_only=True)
    commission_payments = CommissionPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = ChargingSession
        fields = [
            'id',
            'connector',
            'transaction_id',
            'start_time',
            'end_time',
            'meter_start',
            'meter_stop',
            'reservation_id',
            'limit',
            'reason',
            'limit_type',
            'id_tag',
            'stop_id_tag',
            'session_billing',
            'commission_payments'
        ]