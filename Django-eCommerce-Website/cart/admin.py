# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\cart\admin.py

from django.contrib import admin
from .models import Cart, CartItem # Import your Cart and CartItem models

# Register Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['uid', 'user', 'session_key', 'is_paid', 'coupon', 'created_at']
    list_filter = ['is_paid', 'created_at', 'user']
    search_fields = ['user__username', 'session_key', 'uid']
    raw_id_fields = ('user', 'coupon',) # Useful for linking to users and coupons
    readonly_fields = ('uid', 'created_at', 'updated_at') # UID and timestamps are auto-generated

    # Display total items and total price in the list view
    def total_items_display(self, obj):
        return obj.total_items
    total_items_display.short_description = "Total Items"

    def total_price_display(self, obj):
        return f"${obj.get_cart_total():.2f}"
    total_price_display.short_description = "Total Price"

    def get_list_display(self, request):
        # Dynamically add total_items_display and total_price_display to list_display
        # This prevents issues if you modify list_display elsewhere
        return self.list_display + ['total_items_display', 'total_price_display']


# Inline for Cart Items (to view/manage items directly from the Cart admin page)
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0 # Don't show empty forms by default
    fields = ['product', 'color_variant', 'size_variant', 'quantity', 'total_price_display']
    readonly_fields = ['total_price_display'] # total_price is a property, not a database field
    raw_id_fields = ('product', 'color_variant', 'size_variant',) # Useful for linking to products/variants

    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Item Total"


# Register CartItem model (can also be managed via inline in CartAdmin)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['uid', 'cart', 'product', 'quantity', 'total_price_display', 'created_at']
    list_filter = ['created_at', 'cart__is_paid', 'product__category'] # Filter by cart status or product category
    search_fields = ['product__product_name', 'cart__user__username', 'cart__session_key']
    raw_id_fields = ('cart', 'product', 'color_variant', 'size_variant',) # Useful for linking

    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Item Total"