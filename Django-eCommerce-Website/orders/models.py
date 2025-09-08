# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\orders\models.py

from django.db import models
from base.models import BaseModel # assuming this is where your BaseModel is
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Enum for order status
    STATUS_CHOICES = [
        ('processing', 'Processing Payment'),
        ('paid', 'Payment Confirmed'),
        ('preparing', 'Preparing for Shipment'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    def __str__(self):
        return f"Order {self.uid} - {self.status}"