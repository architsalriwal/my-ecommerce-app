# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\home\admin.py

from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem # Import all models

# Register ShippingAddress model
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['uid', 'user', 'full_name', 'address_line1', 'city', 'state', 'postal_code', 'is_default']
    list_filter = ['is_default', 'created_at', 'user']
    search_fields = ['full_name', 'address_line1', 'city', 'postal_code', 'user__username']
    raw_id_fields = ('user',)
    readonly_fields = ('uid', 'created_at', 'updated_at')

# Inline for Order Items (to view/manage items directly from the Order admin page)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Don't show empty forms by default
    # Corrected 'price_at_order' to 'price_at_purchase'
    fields = ['product', 'color_variant', 'size_variant', 'quantity', 'price_at_purchase_display'] 
    # Corrected 'price_at_order' to 'price_at_purchase_display'
    readonly_fields = ['price_at_purchase_display'] 
    raw_id_fields = ('product', 'color_variant', 'size_variant',)

    # Method to display price_at_purchase in the inline
    def price_at_purchase_display(self, obj):
        return f"${obj.price_at_purchase:.2f}"
    price_at_purchase_display.short_description = "Price at Purchase"


# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Corrected 'total_price' to 'total_amount'
    # 'payment_method' is now directly referenced as a field
    list_display = ['uid', 'user', 'total_amount', 'payment_method', 'status', 'payment_status', 'created_at']
    # 'payment_method' is now directly referenced as a field
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at', 'user'] 
    search_fields = ['user__username', 'uid', 'stripe_payment_intent_id']
    raw_id_fields = ('user', 'cart', 'shipping_address', 'coupon',)
    readonly_fields = ('uid', 'created_at', 'updated_at', 'stripe_payment_intent_id', 'stripe_client_secret', 'stripe_charge_id')
    inlines = [OrderItemInline] # Add inline to view order items

    # Method to display total_amount in the list view
    def total_amount(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount.short_description = "Total Amount"


# Register OrderItem model (can also be managed via inline in OrderAdmin)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Corrected 'price_at_order' to 'price_at_purchase'
    list_display = ['uid', 'order', 'product', 'quantity', 'price_at_purchase_display', 'created_at']
    list_filter = ['created_at', 'order__status', 'product__category']
    search_fields = ['product__product_name', 'order__user__username', 'uid']
    raw_id_fields = ('order', 'product', 'color_variant', 'size_variant',)

    # Method to display price_at_purchase in the list view
    def price_at_purchase_display(self, obj):
        return f"${obj.price_at_purchase:.2f}"
    price_at_purchase_display.short_description = "Price at Purchase"