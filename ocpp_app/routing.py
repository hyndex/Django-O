# ocpp_app/routing.py
from django.urls import re_path
from .consumers import OCPPConsumer
from django.urls import path

websocket_urlpatterns = [
    path("ws/meter_values/", MeterValueConsumer.as_asgi()),
    re_path(r'ws/ocpp/(?P<cpid>\w+)/$', OCPPConsumer.as_asgi()),
]

