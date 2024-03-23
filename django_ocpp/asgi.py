# # """
# # ASGI config for django_ocpp project.

# # It exposes the ASGI callable as a module-level variable named ``application``.

# # For more information on this file, see
# # https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
# # """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')

# application = get_asgi_application()


# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import ocpp_app.routing


# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import ocpp_app.routing

# application = ProtocolTypeRouter({
#     "ws": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             ocpp_app.routing.websocket_urlpatterns
#         )
#     ),
# })



# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import ocpp_app.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # Add this line to handle HTTP connections
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             ocpp_app.routing.websocket_urlpatterns
#         )
#     ),
# })


# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import ocpp_app.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             ocpp_app.routing.websocket_urlpatterns
#         )
#     ),
# })

# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import ocpp_app.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             ocpp_app.routing.websocket_urlpatterns
#         )
#     ),
# })



import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import ocpp_app.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ocpp_app.routing.websocket_urlpatterns
        )
    ),
})

