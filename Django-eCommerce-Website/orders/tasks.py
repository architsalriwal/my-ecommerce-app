# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\tasks.py

from celery import shared_task
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order

@shared_task
def process_order_task(order_uid):
    """
    Simulates a long-running order processing task and sends real-time updates
    via WebSockets.
    """
    try:
        order = Order.objects.get(uid=order_uid)
        channel_layer = get_channel_layer()
        channel_name = f"order_{order_uid}" # A unique channel for this order

        # Simulate steps and update status
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {"type": "send_order_status", "status": "Processing Payment", "step": 1, "total_steps": 4}
        )
        time.sleep(3) # Simulate payment processing

        order.status = 'paid'
        order.save()
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {"type": "send_order_status", "status": "Payment Confirmed", "step": 2, "total_steps": 4}
        )
        time.sleep(2) # Simulate inventory check

        order.status = 'preparing'
        order.save()
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {"type": "send_order_status", "status": "Preparing for Shipment", "step": 3, "total_steps": 4}
        )
        time.sleep(4) # Simulate packing

        order.status = 'shipped'
        order.save()
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {"type": "send_order_status", "status": "Shipped!", "step": 4, "total_steps": 4}
        )

        return f"Order {order_uid} processing complete."
        
    except Order.DoesNotExist:
        print(f"Order with UID {order_uid} not found.")
        return f"Order with UID {order_uid} not found."