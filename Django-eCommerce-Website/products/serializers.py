# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\serializers.py

from rest_framework import serializers
from .models import (
    Product, ProductImage, Category, ColorVariant, SizeVariant, 
    Coupon, ProductReview 
)

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images.
    """
    class Meta:
        model = ProductImage
        fields = ['uid', 'image']
        read_only_fields = ['uid']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories.
    """
    class Meta:
        model = Category
        fields = ['uid', 'category_name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'slug', 'created_at', 'updated_at']


class ColorVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for color variants.
    """
    class Meta:
        model = ColorVariant
        fields = ['uid', 'color_name', 'color_code', 'price']
        read_only_fields = ['uid']


class SizeVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for size variants.
    """
    class Meta:
        model = SizeVariant
        fields = ['uid', 'size_name', 'price']
        read_only_fields = ['uid']


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for product reviews.
    Includes username of the reviewer.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    product_uid = serializers.CharField(source='product.uid', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['uid', 'product', 'product_uid', 'user', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['uid', 'user', 'username', 'product', 'product_uid', 'created_at']

    def validate(self, data):
        if data['rating'] < 1 or data['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data


class ProductSerializer(serializers.ModelSerializer):
    """
    Standard serializer for displaying product details.
    Includes nested images, color/size variants, and calculated average rating.
    """
    product_images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    color_variants = ColorVariantSerializer(many=True, read_only=True)
    size_variants = SizeVariantSerializer(many=True, read_only=True)
    
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'uid', 'product_name', 'slug', 'category', 'price', 'product_description',
            'stock', 'product_images', 'color_variants', 'size_variants', 
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'slug', 'created_at', 'updated_at', 'average_rating']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating product instances,
    handling nested image and variant UIDs for association.
    """
    product_image_uids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    color_variant_uids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    size_variant_uids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    category_uid = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Product
        fields = [
            'uid', 'product_name', 'slug', 'category_uid', 'price', 'product_description',
            'stock', 'product_image_uids', 'color_variant_uids', 'size_variant_uids'
        ]
        read_only_fields = ['uid', 'slug']

    def validate_category_uid(self, value):
        try:
            return Category.objects.get(uid=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category with this UID does not exist.")

    def create(self, validated_data):
        product_image_uids = validated_data.pop('product_image_uids', [])
        color_variant_uids = validated_data.pop('color_variant_uids', [])
        size_variant_uids = validated_data.pop('size_variant_uids', [])
        category_instance = validated_data.pop('category_uid')

        product = Product.objects.create(category=category_instance, **validated_data)

        if product_image_uids:
            for img_uid in product_image_uids:
                try:
                    img = ProductImage.objects.get(uid=img_uid)
                    img.product = product
                    img.save()
                except ProductImage.DoesNotExist:
                    print(f"Warning: ProductImage with UID {img_uid} not found.")

        if color_variant_uids:
            color_variants = ColorVariant.objects.filter(uid__in=color_variant_uids)
            product.color_variants.set(color_variants)
        
        if size_variant_uids:
            size_variants = SizeVariant.objects.filter(uid__in=size_variant_uids)
            product.size_variants.set(size_variants)

        return product

    def update(self, instance, validated_data):
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.price = validated_data.get('price', instance.price)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.stock = validated_data.get('stock', instance.stock)

        if 'category_uid' in validated_data:
            instance.category = validated_data.pop('category_uid')

        instance.save()

        if 'color_variant_uids' in validated_data:
            color_variants = ColorVariant.objects.filter(uid__in=validated_data['color_variant_uids'])
            instance.color_variants.set(color_variants)
        
        if 'size_variant_uids' in validated_data:
            size_variants = SizeVariant.objects.filter(uid__in=validated_data['size_variant_uids'])
            instance.size_variants.set(size_variants)
        
        return instance


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for Coupon model.
    """
    class Meta:
        model = Coupon
        fields = [
            'uid', 'coupon_code', 'discount_type', 'discount_amount', 
            'minimum_amount', 'is_active', 'expiry_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at']