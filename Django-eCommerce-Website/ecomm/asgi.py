# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\ecomm\asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from orders import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
