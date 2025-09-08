# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\api_views.py

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated 
from django.shortcuts import get_object_or_404
from django.db import transaction

# Import models (Wishlist removed)
from .models import Product, Category, ColorVariant, SizeVariant, ProductReview
# Import serializers (WishlistSerializer removed)
from .serializers import (
    ProductSerializer, CategorySerializer, ColorVariantSerializer, 
    SizeVariantSerializer, ProductReviewSerializer,
    ProductCreateUpdateSerializer
)


class ProductViewSet(viewsets.ModelViewSet):  #Q6
    """
    A ViewSet for viewing and editing product instances.
    Uses ProductCreateUpdateSerializer for write operations to handle nested data.
    """
    queryset = Product.objects.all().prefetch_related('product_images', 'color_variants', 'size_variants')  
    permission_classes = [AllowAny] 

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    @action(detail=True, methods=['get'])    #Q4
    def reviews(self, request, pk=None):
        """
        Retrieves reviews for a specific product.
        """
        product = get_object_or_404(Product, uid=pk)
        reviews = product.reviews.all().order_by('-created_at')
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ReadOnly ViewSet for viewing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ColorVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ReadOnly ViewSet for viewing color variants.
    """
    queryset = ColorVariant.objects.all()
    serializer_class = ColorVariantSerializer
    permission_classes = [AllowAny]


class SizeVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ReadOnly ViewSet for viewing size variants.
    """
    queryset = SizeVariant.objects.all()
    serializer_class = SizeVariantSerializer
    permission_classes = [AllowAny]


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing product reviews.
    Users can create, update, and delete their own reviews.
    """
    queryset = ProductReview.objects.all().select_related('user', 'product')
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['update', 'partial_update', 'destroy']:
            return queryset.filter(user=self.request.user)
        return queryset
    

