# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\home\models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q 
from base.models import BaseModel 
from products.models import Product, ColorVariant, SizeVariant, Coupon 
from cart.models import Cart # Make sure Cart is imported correctly
from decimal import Decimal # For precise decimal calculations

User = get_user_model() 

# --- ShippingAddress Model ---
class ShippingAddress(BaseModel):
    # This is the missing foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping_addresses")
    full_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Shipping Addresses"
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_default=True),
                name='unique_default_shipping_address'
            )
        ]
        ordering = ['-is_default', 'full_name']

    def __str__(self):
        return f"{self.full_name}, {self.address_line1}, {self.city}, {self.postal_code}"

# --- Order Model ---
class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_orders')
    # Changed from OneToOneField to ForeignKey - a Cart can be associated with an Order
    # but the Cart model itself doesn't need to enforce 1-to-1 for its entire lifecycle.
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders_from_cart") 
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Renamed to total_amount for consistency with API views
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) 
    
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('STRIPE', 'Stripe'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD') # <--- THIS FIELD MUST BE HERE

    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'), # Initial state, might be waiting for payment
        ('Processing', 'Processing'), # Payment received, order being prepared
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
        ('Failed', 'Failed'), # Payment failed
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    
    # Added payment_status field for detailed payment tracking
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'), # Payment initiated, waiting for confirmation
        ('requires_payment_method', 'Requires Payment Method'), # Stripe specific
        ('requires_action', 'Requires Action'), # Stripe specific (e.g., 3D Secure)
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='pending')

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    # NEW STRIPE FIELDS (already present in your code, just ensuring consistency)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    stripe_client_secret = models.CharField(max_length=255, blank=True, null=True) 
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True, unique=True) 

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ['-created_at'] 

    def __str__(self):
        # Convert UID to string before slicing
        return f"Order {str(self.uid)[:8]} by {self.user.username} - {self.status}"

# --- OrderItem Model ---
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    # Renamed to price_at_purchase for consistency
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) 

    class Meta:
        verbose_name_plural = "Order Items"
        unique_together = ('order', 'product', 'color_variant', 'size_variant')

    def __str__(self):
        product_name = self.product.product_name if self.product else "N/A Product"
        order_uid_str = str(self.order.uid)[:8] if self.order and self.order.uid else "N/A" 
        return f"{self.quantity} x {product_name} in Order {order_uid_str}"