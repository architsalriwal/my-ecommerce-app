# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\cart\models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q 
from base.models import BaseModel 
from products.models import Product, ColorVariant, SizeVariant, Coupon 
from decimal import Decimal # <--- ADD THIS IMPORT

User = get_user_model() 

class Cart(BaseModel): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True, db_index=True)
    is_paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Carts" 
        constraints = [
            models.UniqueConstraint(
                fields=['user'], 
                condition=Q(is_paid=False, user__isnull=False), 
                name='unique_active_user_cart'
            ),
            models.UniqueConstraint(
                fields=['session_key'], 
                condition=Q(is_paid=False, session_key__isnull=False), 
                name='unique_active_session_cart'
            ),
        ]

    def get_cart_total(self):
        # Ensure all items' total_price are Decimal before summing
        return sum(item.total_price for item in self.cart_items.all())

    def get_cart_total_price_after_coupon(self):
        total = self.get_cart_total() 
        if self.coupon and total >= self.coupon.minimum_amount:
            total -= self.coupon.discount_amount
                    
        return max(Decimal('0.00'), total) # Ensure return type is Decimal

    @property
    def total_items(self):
        return self.cart_items.count()

    def __str__(self):
        uid_str = str(self.uid)[:8]
        if self.user:
            return f"Cart for {self.user.username} (Paid: {self.is_paid}) (UID: {uid_str})"
        elif self.session_key:
            return f"Anonymous Cart {self.session_key[:5]}... (Paid: {self.is_paid}) (UID: {uid_str})"
        return f"Cart (UID: {uid_str})" 

class CartItem(BaseModel): 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items") 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="cart_items_on_product")
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = "Cart Items" 
        unique_together = ('cart', 'product', 'color_variant', 'size_variant')

    def calculate_item_price(self):
        if not self.product:
            return Decimal('0.00') # <--- CHANGED: Use Decimal for consistency
            
        price = self.product.price

        if self.color_variant:
            price += self.color_variant.price
            
        if self.size_variant:
            price += self.size_variant.price
        
        return price * self.quantity

    @property
    def total_price(self):
        return self.calculate_item_price() 

    def __str__(self):
        product_name = self.product.product_name if self.product else "N/A Product"
        size = self.size_variant.size_name if self.size_variant else "N/A Size"
        color = self.color_variant.color_name if self.color_variant else "N/A Color"
        return f"{self.quantity} x {product_name} ({color}, {size})"