# # C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<order_uid>[0-9a-f-]+)/$', consumers.OrderConsumer.as_asgi()),
]

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the order UID from the URL
        self.order_uid = self.scope['url_route']['kwargs']['order_uid']
        self.order_group_name = f'order_{self.order_uid}'

        # Join the group for this specific order
        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connected for order: {self.order_uid}")

    async def disconnect(self, close_code):
        # Leave the order group
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for order: {self.order_uid}")

    # Receive message from channel layer
    async def send_order_status(self, event):
        status = event['status']
        step = event.get('step')
        total_steps = event.get('total_steps')
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'status': status,
            'step': step,
            'total_steps': total_steps
        }))