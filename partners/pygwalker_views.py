from djangoaddicts.pygwalker.views import PygWalkerView
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from django.db.models import Sum
import csv

from .models import (
    PartnerCommissionMemberGroup,
    PartnerCommissionMember,
    BankAccount,
    Settlement,
    SettlementRequest,
    PartnerEmployeeList,
    UserPartnerEmployeeList,
    CommissionPayment,
)

from ocpp_app.models import ChargingSession
from .serializers import (
    PartnerCommissionMemberGroupSerializer,
    PartnerCommissionMemberSerializer,
    BankAccountSerializer,
    SettlementSerializer,
    SettlementRequestSerializer,
    PartnerEmployeeListSerializer,
    UserPartnerEmployeeListSerializer,
    ChargingSessionSerializer
)

class PartnerCommissionMemberGroupPygWalkerView(PygWalkerView):
    serializer_class = PartnerCommissionMemberGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PartnerCommissionMemberGroup.objects.filter(commission_members__user=user)


class PartnerCommissionMemberPygWalkerView(PygWalkerView):
    serializer_class = PartnerCommissionMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PartnerCommissionMember.objects.filter(user=user)


class BankAccountPygWalkerView(PygWalkerView):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BankAccount.objects.filter(partner_commission_member__user=user)


class SettlementPygWalkerView(PygWalkerView):
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Settlement.objects.filter(partner_commission_member__user=user)


class SettlementRequestPygWalkerView(PygWalkerView):
    serializer_class = SettlementRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SettlementRequest.objects.filter(partner_commission_member__user=user)


class PartnerEmployeeListPygWalkerView(PygWalkerView):
    serializer_class = PartnerEmployeeListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PartnerEmployeeList.objects.filter(partner_commission_member_group__commission_members__user=user)


class UserPartnerEmployeeListPygWalkerView(PygWalkerView):
    serializer_class = UserPartnerEmployeeListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserPartnerEmployeeList.objects.filter(host_custom_user_list__partner_commission_member_group__commission_members__user=user)


class ChargingSessionPygWalkerView(PygWalkerView):
    serializer_class = ChargingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChargingSession.objects.filter(connector__charger__charger_commission_group__commission_members__user=user)
