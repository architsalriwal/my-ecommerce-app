from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import ShippingAddress, Order, OrderItem
from cart.models import Cart
from products.models import Product, ColorVariant, SizeVariant, Coupon
from products.serializers import CouponSerializer

User = get_user_model()

class ShippingAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShippingAddress
        fields = [
            'uid', 'user', 'full_name', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'phone_number',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    color_name = serializers.CharField(source='color_variant.color_name', read_only=True, allow_null=True)
    size_name = serializers.CharField(source='size_variant.size_name', read_only=True, allow_null=True)

    class Meta:
        model = OrderItem
        fields = [
            'uid', 'product_name', 'color_name', 'size_name', 'quantity', 'price_at_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    shipping_address_detail = ShippingAddressSerializer(source='shipping_address', read_only=True)
    coupon_detail = CouponSerializer(source='coupon', read_only=True)

    class Meta:
        model = Order
        fields = [
            'uid', 'user', 'user_username', 'shipping_address', 'shipping_address_detail',
            'total_amount', 'payment_method', 'status', 'payment_status', 'order_items', 'coupon', 'coupon_detail',
            'created_at', 'updated_at', 'stripe_payment_intent_id', 'stripe_client_secret', 'stripe_charge_id'
        ]
        read_only_fields = [
            'uid', 'user', 'user_username', 'shipping_address', 'shipping_address_detail',
            'total_amount', 'payment_method', 'status', 'payment_status', 'order_items',
            'coupon', 'coupon_detail', 'created_at', 'updated_at',
            'stripe_payment_intent_id', 'stripe_client_secret', 'stripe_charge_id'
        ]

class OrderCreateSerializer(serializers.Serializer):
    cart_uid = serializers.UUIDField(write_only=True, required=True)
    shipping_address_uid = serializers.UUIDField(write_only=True, required=True)
    payment_method = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to place an order.")

        cart_uid = data.get('cart_uid')
        shipping_address_uid = data.get('shipping_address_uid')
        payment_method = data.get('payment_method')
        
        # --- Debugging print statements start here ---
        print(f"Attempting to find cart with UID: {cart_uid}")
        print(f"Authenticated user: {request.user.username} (ID: {request.user.id})")
        # --- Debugging print statements end here ---

        # Inside OrderCreateSerializer's validate method
        print(f"DEBUG: Authenticated user ID: {request.user.id}")
        print(f"DEBUG: Request payload cart_uid: {cart_uid}")
        try:
            cart = Cart.objects.get(uid=cart_uid, user=request.user, is_paid=False)
            if not cart.cart_items.exists():
                raise serializers.ValidationError({"cart_uid": "Cart is empty."})
            data['cart'] = cart
            # After the try block, add a success print statement        
            print(f"DEBUG: Successfully validated cart {cart_uid} for user {request.user.id}")
        
        except Cart.DoesNotExist:
            print(f"Cart with UID {cart_uid} not found for user {request.user.username} or is already paid.")
            raise serializers.ValidationError({"cart_uid": "Active cart not found for this user."})
        
        try:
            shipping_address = ShippingAddress.objects.get(uid=shipping_address_uid, user=request.user)
            data['shipping_address'] = shipping_address
        except ShippingAddress.DoesNotExist:
            raise serializers.ValidationError({"shipping_address_uid": "Shipping address not found or does not belong to user."})
        
        valid_payment_methods = ['COD', 'STRIPE']
        payment_method = payment_method.upper()
        if payment_method not in valid_payment_methods:
            raise serializers.ValidationError(
                {"payment_method": f"Invalid payment method. Choose from: {', '.join(valid_payment_methods)}"}
            )
        
        # Check for stock availability for all cart items
        for cart_item in cart.cart_items.all():
            if not cart_item.product:
                raise serializers.ValidationError(f"Product not found for item {str(cart_item.uid)[:8]}. Please remove this item.")
            if cart_item.product.stock < cart_item.quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {cart_item.product.product_name}. Available: {cart_item.product.stock}, Requested: {cart_item.quantity}"
                )

        data['payment_method'] = payment_method
        return data

    def create(self, validated_data):
        """
        Creates a new order. This method is designed for COD orders.
        """
        user = self.context['request'].user
        cart = validated_data.pop('cart')
        shipping_address = validated_data.pop('shipping_address')
        payment_method = validated_data.pop('payment_method')

        if payment_method != 'COD':
            raise serializers.ValidationError("This serializer's create method is for COD payments only.")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                cart=cart,
                shipping_address=shipping_address,
                total_amount=cart.get_cart_total_price_after_coupon(),
                payment_method=payment_method,
                status='Processing',
                payment_status='succeeded',
                coupon=cart.coupon
            )

            # Create OrderItems and reduce product stock
            for cart_item in cart.cart_items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    color_variant=cart_item.color_variant,
                    size_variant=cart_item.size_variant,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.total_price / cart_item.quantity
                )
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Mark cart as paid
            cart.is_paid = True
            cart.save()
            
            return order
