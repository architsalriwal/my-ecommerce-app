# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<order_uid>[0-9a-f-]+)/$', consumers.OrderConsumer.as_asgi()),
]
