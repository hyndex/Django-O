# urls.py

from django.urls import path
from .views import OCPIVersionsView, OCPIChargerLocationView, OCPISessionView, OCPICDRView, OCPITokenView

urlpatterns = [
    path('ocpi/versions', OCPIVersionsView.as_view(), name='ocpi_versions'),
    path('ocpi/2.2/locations', OCPIChargerLocationView.as_view(), name='ocpi_locations'),
    path('ocpi/2.2/sessions', OCPISessionView.as_view(), name='ocpi_sessions'),
    path('ocpi/2.2/sessions/<str:session_id>', OCPISessionView.as_view(), name='ocpi_session_details'),
    path('ocpi/2.2/cdrs', OCPICDRView.as_view(), name='ocpi_cdrs'),
    path('ocpi/2.2/tokens/<str:token_uid>', OCPITokenView.as_view(), name='ocpi_tokens'),
]
