from django.urls import path
from .consumers import OCPPConsumer

websocket_urlpatterns = [
    path('ws/ocpp/', OCPPConsumer.as_asgi()),
]
