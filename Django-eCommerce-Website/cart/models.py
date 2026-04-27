# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\cart\models.py

# ===================== IMPORTS =====================

# Aggregate functions (SUM), field references (F expressions)
from django.db.models import Sum, F  

# Used to replace NULL values with a default (very important for calculations)
from django.db.models.functions import Coalesce  

# Core Django model utilities
from django.db import models  

# Get the active User model (default or custom)
from django.contrib.auth import get_user_model  

# Used to create conditional constraints
from django.db.models import Q  

# BaseModel likely contains common fields like uid, created_at, etc.
from base.models import BaseModel  

# Importing related models used in cart
from products.models import Product, ColorVariant, SizeVariant, Coupon  

# Decimal is used instead of float for money (VERY IMPORTANT for accuracy)
from decimal import Decimal  

# Get the User model
User = get_user_model()  


# ===================== CART MODEL =====================

class Cart(BaseModel):
    """
    This model represents a shopping cart.
    
    A cart can belong to:
    1. A logged-in user (user field)
    2. An anonymous user (session_key field)
    
    Only ONE active (not paid) cart is allowed per user/session.
    """

    # If user is logged in → cart is linked to user
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="carts", 
        null=True, 
        blank=True
    )

    # If user is NOT logged in → cart is tracked using session_key
    # db_index=True → makes searching faster in database
    session_key = models.CharField(
        max_length=40, 
        null=True, 
        blank=True, 
        unique=True, 
        db_index=True
    )

    # Whether the cart has been converted into an order
    is_paid = models.BooleanField(default=False)

    # Optional coupon applied to the cart
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name_plural = "Carts"

        """
        CONSTRAINTS → Ensure data consistency
        
        These constraints ensure:
        - A user can have ONLY ONE active cart (is_paid=False)
        - A session can have ONLY ONE active cart
        """

        constraints = [

            # 1️⃣ Only one active cart per user
            models.UniqueConstraint(
                fields=['user'], 
                condition=Q(is_paid=False, user__isnull=False), 
                name='unique_active_user_cart'
            ),

            # 2️⃣ Only one active cart per session
            models.UniqueConstraint(
                fields=['session_key'], 
                condition=Q(is_paid=False, session_key__isnull=False), 
                name='unique_active_session_cart'
            ),
        ]


    # ===================== CORE BUSINESS LOGIC =====================

    def get_cart_total(self):
        """
        Calculate total price of the cart using DATABASE (PostgreSQL)

        WHY this approach?
        - Faster than Python loops
        - Avoids multiple queries (optimized)
        - Uses SQL JOIN + aggregation

        Formula per item:
        (product price + color price + size price) * quantity
        """

        result = self.cart_items.annotate(

            # Calculate price per cart item
            item_total=(

                # Base product price
                F('product__price') +

                # Add color price (if NULL → treat as 0)
                Coalesce(F('color_variant__price'), Decimal('0.00')) +

                # Add size price (if NULL → treat as 0)
                Coalesce(F('size_variant__price'), Decimal('0.00'))

            ) * F('quantity')  # Multiply by quantity

        ).aggregate(

            # Sum all item totals
            cart_total=Sum('item_total')

        )

        # If cart is empty → return 0 instead of None
        return result['cart_total'] or Decimal('0.00')


    def get_cart_total_price_after_coupon(self):
        """
        Apply coupon logic on top of total cart value
        
        Steps:
        1. Get total cart value
        2. Check if coupon exists
        3. Check minimum amount condition
        4. Apply discount
        5. Ensure total never goes below 0
        """

        total = self.get_cart_total()

        if self.coupon and total >= self.coupon.minimum_amount:
            total -= self.coupon.discount_amount

        # Ensure total is never negative
        return max(Decimal('0.00'), total)


    @property
    def total_items(self):
        """
        Returns total number of items in cart
        
        NOTE:
        This counts rows, NOT quantities.
        Example:
        - 2 items with quantity 3 each → count = 2 (not 6)
        """
        return self.cart_items.count()


    def __str__(self):
        """
        String representation (for Django admin/debugging)
        """

        uid_str = str(self.uid)[:8]  # Short UID for readability

        if self.user:
            return f"Cart for {self.user.username} (Paid: {self.is_paid}) (UID: {uid_str})"

        elif self.session_key:
            return f"Anonymous Cart {self.session_key[:5]}... (Paid: {self.is_paid}) (UID: {uid_str})"

        return f"Cart (UID: {uid_str})"


# ===================== CART ITEM MODEL =====================

class CartItem(BaseModel):
    """
    Represents a single item inside a cart.
    
    Example:
    Cart → contains multiple CartItems
    Each CartItem → specific product + variant + quantity
    """

    # Link to Cart
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name="cart_items"
    )

    # Product reference
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="cart_items_on_product"
    )

    # Optional color variant
    color_variant = models.ForeignKey(
        ColorVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # Optional size variant
    size_variant = models.ForeignKey(
        SizeVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # Quantity of this item
    quantity = models.PositiveIntegerField(default=1)


    class Meta:
        verbose_name_plural = "Cart Items"

        """
        UNIQUE CONSTRAINT:
        Prevent duplicate entries like:
        Same product + same color + same size in same cart
        
        Instead of duplicate rows → quantity should increase
        """
        unique_together = ('cart', 'product', 'color_variant', 'size_variant')


    # ===================== PRICE CALCULATION =====================

    def calculate_item_price(self):
        """
        Calculate price of THIS cart item
        
        Formula:
        (product price + color price + size price) * quantity
        """

        # If product is deleted or missing
        if not self.product:
            return Decimal('0.00')

        # Start with base product price
        price = self.product.price

        # Add color price if exists
        if self.color_variant:
            price += self.color_variant.price

        # Add size price if exists
        if self.size_variant:
            price += self.size_variant.price

        # Multiply by quantity
        return price * self.quantity


    @property
    def total_price(self):
        """
        Property so you can access like:
        cart_item.total_price instead of calling function
        """
        return self.calculate_item_price()


    def __str__(self):
        """
        String representation for debugging/admin
        """

        product_name = self.product.product_name if self.product else "N/A Product"
        size = self.size_variant.size_name if self.size_variant else "N/A Size"
        color = self.color_variant.color_name if self.color_variant else "N/A Color"

        return f"{self.quantity} x {product_name} ({color}, {size})"
    

