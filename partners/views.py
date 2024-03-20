from rest_framework import viewsets, permissions, mixins
from .models import (ChargerOwner, BankAccount, Settlement, SettlementRequest,
                     PartnerCommissionGroup, PartnerCommission, PartnerCommissionGroupUser,
                     PartnerEmployeeList, UserPartnerEmployeeList)
from .serializers import (ChargerOwnerSerializer, BankAccountSerializer, SettlementSerializer,
                          SettlementRequestSerializer, PartnerCommissionGroupSerializer,
                          PartnerCommissionSerializer, PartnerCommissionGroupUserSerializer,
                          PartnerEmployeeListSerializer, UserPartnerEmployeeListSerializer)

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
