from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PartnerCommissionMemberGroupViewSet,
    PartnerCommissionMemberViewSet,
    BankAccountViewSet,
    SettlementViewSet,
    SettlementRequestViewSet,
    PartnerEmployeeListViewSet,
    UserPartnerEmployeeListViewSet,
    ChargingSessionViewSet,
)

# Creating a router and registering our viewsets
router = DefaultRouter()
router.register('partner-commission-member-groups', PartnerCommissionMemberGroupViewSet)
router.register('partner-commission-members', PartnerCommissionMemberViewSet)
router.register('bank-accounts', BankAccountViewSet)
router.register('settlements', SettlementViewSet)
router.register('settlement-requests', SettlementRequestViewSet)
router.register('partner-employee-lists', PartnerEmployeeListViewSet)
router.register('user-partner-employee-lists', UserPartnerEmployeeListViewSet)
router.register('charging-sessions', ChargingSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Includes router-generated URL patterns
    # Custom action for requesting settlement
    path('partner-commission-members/<int:pk>/request_settlement/', 
         PartnerCommissionMemberViewSet.as_view({'post': 'request_settlement'}), 
         name='partner-commission-member-request-settlement'),
    # Custom action for exporting charging sessions to CSV
    path('charging-sessions/export_csv/', 
         ChargingSessionViewSet.as_view({'get': 'export_csv'}), 
         name='charging-sessions-export-csv'),
]
