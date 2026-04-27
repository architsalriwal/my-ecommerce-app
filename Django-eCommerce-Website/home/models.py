# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\home\models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q 
from base.models import BaseModel 
from products.models import Product, ColorVariant, SizeVariant, Coupon 
from cart.models import Cart 
from decimal import Decimal 

# Get the custom User model (important for flexibility)
User = get_user_model() 


# ============================================================
# 🏠 SHIPPING ADDRESS MODEL
# ============================================================
# This model stores all addresses saved by a user.
# A user can have multiple addresses, but only ONE can be default.
# ============================================================

class ShippingAddress(BaseModel):

    # 🔗 Each address belongs to a specific user
    # CASCADE → If user is deleted, all their addresses are deleted
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="shipping_addresses"
    )

    # 👤 Basic user details for delivery
    full_name = models.CharField(max_length=255)

    # 📍 Address fields
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    # 📞 Optional contact number
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # ⭐ Only ONE address per user can be default
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Shipping Addresses"

        # 🚨 IMPORTANT CONSTRAINT:
        # Ensures only ONE default address per user
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_default=True),
                name='unique_default_shipping_address'
            )
        ]

        # 🔽 Default ordering → default address first
        ordering = ['-is_default', 'full_name']

    def __str__(self):
        return f"{self.full_name}, {self.address_line1}, {self.city}, {self.postal_code}"


# ============================================================
# 🛒 ORDER MODEL
# ============================================================
# This represents a completed or in-progress order.
# It is created when user proceeds to checkout.
# ============================================================

class Order(BaseModel):

    # 🔗 Order belongs to a user (must be logged in)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='home_orders'
    )

    # 🔗 Link to the Cart from which this order was created
    # SET_NULL → If cart is deleted, order still remains
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="orders_from_cart"
    )

    # 📦 Shipping address used for this order
    shipping_address = models.ForeignKey(
        ShippingAddress, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # 💰 Total price of the order
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) 


    # ============================================================
    # 💳 PAYMENT METHOD
    # ============================================================
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('STRIPE', 'Stripe'),
    ]

    # Default is COD (offline payment)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='COD'
    )


    # ============================================================
    # 📦 ORDER STATUS (Business Flow)
    # ============================================================
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),       # Order created, waiting for payment
        ('Processing', 'Processing'), # Payment done, preparing order
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
        ('Failed', 'Failed'),         # Payment failed
    ]

    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='Pending'
    )


    # ============================================================
    # 💰 PAYMENT STATUS (Especially for Stripe)
    # ============================================================
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('requires_payment_method', 'Requires Payment Method'),
        ('requires_action', 'Requires Action'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment_status = models.CharField(
        max_length=30, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )


    # 🎟️ Optional coupon applied to order
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )


    # ============================================================
    # 💳 STRIPE INTEGRATION FIELDS
    # ============================================================

    # Unique ID from Stripe (used in webhook verification)
    stripe_payment_intent_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True
    )

    # Used by frontend to complete payment
    stripe_client_secret = models.CharField(
        max_length=255, 
        blank=True, 
        null=True
    ) 

    # Final charge ID after successful payment
    stripe_charge_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True
    ) 


    class Meta:
        verbose_name_plural = "Orders"

        # 🔽 Latest orders first
        ordering = ['-created_at'] 

    def __str__(self):
        return f"Order {str(self.uid)[:8]} by {self.user.username} - {self.status}"


# ============================================================
# 📦 ORDER ITEM MODEL
# ============================================================
# Represents individual products inside an order
# (like line items in a bill)
# ============================================================

class OrderItem(BaseModel):

    # 🔗 Each item belongs to an Order
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="order_items"
    )

    # 🛍️ Product purchased
    # SET_NULL → keeps order history even if product is deleted
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True
    )

    # 🎨 Optional variants
    color_variant = models.ForeignKey(
        ColorVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    size_variant = models.ForeignKey(
        SizeVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # 🔢 Quantity of product
    quantity = models.PositiveIntegerField(default=1)

    # 💰 Price at time of purchase
    # IMPORTANT: This ensures price history is preserved
    price_at_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    ) 

    class Meta:
        verbose_name_plural = "Order Items"

        # 🚨 Prevent duplicate entries like:
        # Same product + same variants in same order
        unique_together = ('order', 'product', 'color_variant', 'size_variant')

    def __str__(self):
        product_name = self.product.product_name if self.product else "N/A Product"
        order_uid_str = str(self.order.uid)[:8] if self.order and self.order.uid else "N/A" 
        return f"{self.quantity} x {product_name} in Order {order_uid_str}"