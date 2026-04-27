# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\routing.py

from django.urls import re_path
from . import consumers

# This works like urls.py but for WebSockets instead of HTTP
websocket_urlpatterns = [

    # Example URL:
    # ws://localhost:8000/ws/order/123e4567-e89b-12d3-a456/

    re_path(
        r'ws/order/(?P<order_uid>[0-9a-f-]+)/$',  # Extract order_uid from URL
        consumers.OrderConsumer.as_asgi()         # Route to this consumer
    ),
]