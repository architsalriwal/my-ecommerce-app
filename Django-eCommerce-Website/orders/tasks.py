# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\tasks.py

# Import Celery decorator to create async background tasks
from celery import shared_task

# Used to simulate delay (like real-world processing time)
import time

# This gives us access to Redis (Channel Layer)
from channels.layers import get_channel_layer

# This is the bridge between sync (Celery/Django) and async (WebSockets)
from asgiref.sync import async_to_sync

# Your Order model (database table)
from .models import Order


@shared_task
def process_order_task(order_uid):
    """
    This function runs in the background (Celery worker).
    
    Its job:
    1. Simulate order processing (like payment, packaging, shipping)
    2. Update database status
    3. Send real-time updates to frontend via WebSockets
    """
    try:
        # STEP 1: Fetch the order from DB using order_uid
        order = Order.objects.get(uid=order_uid)

        # STEP 2: Get the channel layer (Redis connection)
        # This allows us to send messages to WebSocket consumers
        channel_layer = get_channel_layer()

        # STEP 3: Define a unique group name for this order
        # IMPORTANT: This must match what consumer is using
        channel_name = f"order_{order_uid}"


        # ============================
        # STEP 1: PAYMENT PROCESSING
        # ============================

        # Send message to WebSocket group (React clients listening)
        async_to_sync(channel_layer.group_send)(
            channel_name,  # Target group (all users watching this order)

            # This dictionary is the "event" sent to consumer
            {
                "type": "send_order_status",  # MUST match consumer function name
                "status": "Processing Payment",
                "step": 1,
                "total_steps": 4
            }
        )

        # Simulate delay (real-world: Stripe/payment gateway time)
        time.sleep(3)


        # Update DB status
        order.status = 'paid'
        order.save()

        # Notify frontend
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {
                "type": "send_order_status",
                "status": "Payment Confirmed",
                "step": 2,
                "total_steps": 4
            }
        )

        time.sleep(2)


        # ============================
        # STEP 2: PREPARING ORDER
        # ============================

        order.status = 'preparing'
        order.save()

        async_to_sync(channel_layer.group_send)(
            channel_name,
            {
                "type": "send_order_status",
                "status": "Preparing for Shipment",
                "step": 3,
                "total_steps": 4
            }
        )

        time.sleep(4)


        # ============================
        # STEP 3: SHIPPING
        # ============================

        order.status = 'shipped'
        order.save()

        async_to_sync(channel_layer.group_send)(
            channel_name,
            {
                "type": "send_order_status",
                "status": "Shipped!",
                "step": 4,
                "total_steps": 4
            }
        )

        # Final return (Celery logs this)
        return f"Order {order_uid} processing complete."


    except Order.DoesNotExist:
        # If order not found in DB
        print(f"Order with UID {order_uid} not found.")
        return f"Order with UID {order_uid} not found."