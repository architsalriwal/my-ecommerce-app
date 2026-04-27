# # C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\routing.py

import json

# Base class for async WebSocket handling
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """
        Called when frontend (React) opens WebSocket connection
        """

        # STEP 1: Extract order_uid from URL
        # Example: ws://.../ws/order/123/
        self.order_uid = self.scope['url_route']['kwargs']['order_uid']

        # STEP 2: Create group name
        self.order_group_name = f'order_{self.order_uid}'

        # STEP 3: Add this connection to group
        # Means: "This user is interested in updates for this order"
        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name   # unique ID of this connection
        )

        # STEP 4: Accept WebSocket connection
        await self.accept()

        print(f"WebSocket connected for order: {self.order_uid}")
        # THE SENIOR FIX: Fetch current state on connect/reconnect!
        from orders.models import Order
        from asgiref.sync import sync_to_async
        
        try:
            # Query the DB to see if they missed anything while offline
            order = await sync_to_async(Order.objects.get)(uid=self.order_uid)
            
            # Instantly update their screen to the real database state
            await self.send(text_data=json.dumps({
                'status': order.status,
                'message': 'Connected and synced.'
            }))
        except Order.DoesNotExist:
            pass


    async def disconnect(self, close_code):
        """
        Called when user closes browser / connection drops
        """

        # Remove user from group
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )

        print(f"WebSocket disconnected for order: {self.order_uid}")


    async def send_order_status(self, event):
        """
        This function is triggered when Redis sends a message
        
        IMPORTANT:
        The 'type' field in group_send MUST match this function name
        """

        # Extract data from event (sent by Celery/Django)
        status = event['status']
        step = event.get('step')  # optional
        total_steps = event.get('total_steps')  # optional

        # Send data to frontend via WebSocket
        await self.send(text_data=json.dumps({
            'status': status,
            'step': step,
            'total_steps': total_steps
        }))