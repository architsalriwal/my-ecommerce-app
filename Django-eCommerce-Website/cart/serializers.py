# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\cart\serializers.py

from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer, ColorVariantSerializer, SizeVariantSerializer, CouponSerializer
from products.models import Product, ColorVariant, SizeVariant, Coupon

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    color_variant_detail = ColorVariantSerializer(source='color_variant', read_only=True)
    size_variant_detail = SizeVariantSerializer(source='size_variant', read_only=True)
    item_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='total_price')

    class Meta:
        model = CartItem
        fields = [
            'uid', 'product', 'product_detail', 'color_variant', 'color_variant_detail',
            'size_variant', 'size_variant_detail', 'quantity', 'item_total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields 


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    product_uid = serializers.UUIDField(write_only=True, required=True) 
    color_variant_uid = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    size_variant_uid = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CartItem
        fields = [
            'uid', 'product_uid', 'color_variant_uid', 'size_variant_uid', 'quantity', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at'] 
        extra_kwargs = {
            'quantity': {'required': True} 
        }

    def validate(self, data):
        if 'cart' not in self.context:
            raise serializers.ValidationError("Cart instance must be provided in serializer context.")
        
        request = self.context.get('request')

        try:
            product_uid = data.get('product_uid')
            product = Product.objects.get(uid=product_uid)
            data['product'] = product 
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_uid": "Product not found."})

        color_variant = None
        if data.get('color_variant_uid'):
            try:
                color_variant = ColorVariant.objects.get(uid=data['color_variant_uid'])
                data['color_variant'] = color_variant
            except ColorVariant.DoesNotExist:
                raise serializers.ValidationError({"color_variant_uid": "Color variant not found."})

        size_variant = None
        if data.get('size_variant_uid'):
            try:
                size_variant = SizeVariant.objects.get(uid=data['size_variant_uid'])
                data['size_variant'] = size_variant
            except SizeVariant.DoesNotExist:
                raise serializers.ValidationError({"size_variant_uid": "Size variant not found."})

        quantity = data.get('quantity')
        if product.stock < quantity:
            raise serializers.ValidationError(f"Insufficient stock for {product.product_name}. Available: {product.stock}, Requested: {quantity}.")

        return data

    def create(self, validated_data):
        cart = self.context['cart'] 
        product = validated_data.pop('product') 
        color_variant = validated_data.pop('color_variant', None) 
        size_variant = validated_data.pop('size_variant', None) 
        quantity = validated_data.pop('quantity', 1) 

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color_variant=color_variant,
            size_variant=size_variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True) 
    user_username = serializers.CharField(source='user.username', read_only=True)
    coupon_detail = CouponSerializer(source='coupon', read_only=True)

    total_cart_items = serializers.IntegerField(read_only=True, source='total_items')
    total_cart_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_cart_total')
    total_price_after_coupon = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_cart_total_price_after_coupon')

    class Meta:
        model = Cart
        fields = [
            'uid', 'user', 'user_username', 'coupon', 'coupon_detail', 'is_paid',
            'cart_items', 'total_cart_items', 'total_cart_price', 'total_price_after_coupon',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'uid', 'user', 'user_username', 'coupon', 'coupon_detail', 'is_paid',
            'total_cart_items', 'total_cart_price', 'total_price_after_coupon',
            'created_at', 'updated_at'
        ]

class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required=True)

    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(coupon_code=value, is_active=True)
            self.instance = coupon 
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired coupon code.")
        return value

    def validate(self, data):
        if 'cart' not in self.context:
            raise serializers.ValidationError("Cart instance must be provided in serializer context.")
        
        cart = self.context['cart']
        coupon = self.instance 

        if cart.coupon == coupon:
            raise serializers.ValidationError("This coupon is already applied to your cart.")
        
        if cart.get_cart_total() < coupon.minimum_amount:
            raise serializers.ValidationError(
                f"Cart total must be at least ${coupon.minimum_amount:.2f} to apply this coupon."
            )

        data['coupon'] = coupon 
        return data