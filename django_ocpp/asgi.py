# """
# ASGI config for django_ocpp project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
# """

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')

application = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ocpp_app.routing


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ocpp_app.routing

application = ProtocolTypeRouter({
    "ws": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ocpp_app.routing.websocket_urlpatterns
        )
    ),
})
