from pygwalker.decorators import pygwalker_view
from .models import ChargingSession, Settlement, CommissionPayment
from .serializers import ChargingSessionSerializer, SettlementSerializer, CommissionPaymentSerializer
from rest_framework import viewsets, permissions

@pygwalker_view
class ChargingSessionPygwalkerViewSet(viewsets.ModelViewSet):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

@pygwalker_view
class SettlementPygwalkerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated]

@pygwalker_view
class CommissionPaymentPygwalkerViewSet(viewsets.ModelViewSet):
    queryset = CommissionPayment.objects.all()
    serializer_class = CommissionPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
