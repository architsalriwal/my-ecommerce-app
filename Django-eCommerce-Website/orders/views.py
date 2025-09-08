# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .tasks import process_order_task
from .models import Order # Assuming you have an Order model

@csrf_exempt
def create_order_and_process(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # You would replace this with your actual order creation logic.
            # For this example, we'll create a dummy order object.
            
            # This is a critical step: create a new order in your database
            # and get its unique ID (like a UUID).
            order = Order.objects.create(status='pending', user_id=1) # Replace with actual user ID
            
            # Dispatch the Celery task with the unique order UID
            process_order_task.delay(str(order.uid))
            
            # Return the order UID to the frontend so it can connect to the right WebSocket
            return JsonResponse({'order_uid': str(order.uid)}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
