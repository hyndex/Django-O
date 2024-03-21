from rest_framework import viewsets, permissions, mixins
from .models import (ChargerOwner, BankAccount, Settlement, SettlementRequest,
                     PartnerCommissionGroup, PartnerCommission, PartnerCommissionGroupUser,
                     PartnerEmployeeList, UserPartnerEmployeeList)
from .serializers import (ChargerOwnerSerializer, BankAccountSerializer, SettlementSerializer,
                          SettlementRequestSerializer, PartnerCommissionGroupSerializer,
                          PartnerCommissionSerializer, PartnerCommissionGroupUserSerializer,
                          PartnerEmployeeListSerializer, UserPartnerEmployeeListSerializer)



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import PartnerCommissionMember, BankAccount, SettlementRequest, CommissionPayment, UserPartnerEmployeeList, ChargingSession
from .serializers import PartnerCommissionMemberSerializer, BankAccountSerializer, SettlementRequestSerializer, UserPartnerEmployeeListSerializer, ChargingSessionSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
import csv
from django.http import HttpResponse


class ChargerOwnerViewSet(viewsets.ModelViewSet):
    queryset = ChargerOwner.objects.all()
    serializer_class = ChargerOwnerSerializer
    permission_classes = [permissions.IsAuthenticated]

class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BankAccount.objects.filter(owner__user=user)

    def perform_create(self, serializer):
        instance = serializer.save()
        # Log the creation of the bank account

class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated]

class SettlementRequestViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    queryset = SettlementRequest.objects.all()
    serializer_class = SettlementRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartnerCommissionGroupViewSet(viewsets.ModelViewSet):
    queryset = PartnerCommissionGroup.objects.all()
    serializer_class = PartnerCommissionGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartnerCommissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartnerCommissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PartnerCommission.objects.filter(user=user)

class PartnerCommissionGroupUserViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerCommissionGroupUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PartnerCommissionGroupUser.objects.filter(user=user)

class PartnerEmployeeListViewSet(viewsets.ModelViewSet):
    queryset = PartnerEmployeeList.objects.all()
    serializer_class = PartnerEmployeeListSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserPartnerEmployeeListViewSet(viewsets.ModelViewSet):
    serializer_class = UserPartnerEmployeeListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserPartnerEmployeeList.objects.filter(user=user)



class PartnerCommissionMemberViewSet(viewsets.ModelViewSet):
    queryset = PartnerCommissionMember.objects.all()
    serializer_class = PartnerCommissionMemberSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def request_settlement(self, request, pk=None):
        commission_member = self.get_object()
        unpaid_commissions = CommissionPayment.objects.filter(partner_commission_member=commission_member, status='UNPAID')
        total_amount = unpaid_commissions.aggregate(Sum('amount'))['amount__sum'] or 0

        if total_amount > 0:
            settlement_request = SettlementRequest.objects.create(amount=total_amount, status='Requested', partner_commission_member=commission_member)
            unpaid_commissions.update(status='In Process', settlement_request=settlement_request)
            return JsonResponse({'message': 'Settlement requested successfully', 'settlement_request_id': settlement_request.id})
        else:
            return JsonResponse({'error': 'No unpaid commissions to settle'}, status=400)

class UserPartnerEmployeeListViewSet(viewsets.ModelViewSet):
    queryset = UserPartnerEmployeeList.objects.all()
    serializer_class = UserPartnerEmployeeListSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if UserPartnerEmployeeList.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'error': 'Employee with this phone number already exists'}, status=400)
        return super().create(request, *args, **kwargs)

class ChargingSessionViewSet(viewsets.ModelViewSet):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="charging_sessions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Transaction ID', 'Start Time', 'End Time', 'Meter Start', 'Meter Stop', 'Amount Added', 'Amount Consumed', 'Amount Refunded'])

        for session in self.get_queryset():
            writer.writerow([
                session.transaction_id,
                session.start_time,
                session.end_time,
                session.meter_start,
                session.meter_stop,
                session.billings.amount_added,
                session.billings.amount_consumed,
                session.billings.amount_refunded,
            ])

        return response
