# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\api_views.py

# products/api_views.py

# =========================
# DRF IMPORTS
# =========================

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated 

# =========================
# DJANGO IMPORTS
# =========================

from django.shortcuts import get_object_or_404
from django.db import transaction

# =========================
# MODELS IMPORT
# =========================

# These are your database tables
from .models import Product, Category, ColorVariant, SizeVariant, ProductReview

# =========================
# SERIALIZERS IMPORT
# =========================

# Serializers convert:
# Python objects <--> JSON (API response/request)
from .serializers import (
    ProductSerializer, CategorySerializer, ColorVariantSerializer, 
    SizeVariantSerializer, ProductReviewSerializer,
    ProductCreateUpdateSerializer
)


# ==========================================================
# PRODUCT VIEWSET
# ==========================================================

class ProductViewSet(viewsets.ModelViewSet):  # Q6
    """
    This ViewSet handles ALL operations related to Product:
    
    - GET /products/          → List all products
    - GET /products/{id}/     → Get single product
    - POST /products/         → Create product
    - PUT /products/{id}/     → Update product
    - DELETE /products/{id}/  → Delete product

    Think of this as: FULL CRUD API for products
    """

    # =========================
    # QUERYSET (DATA SOURCE)
    # =========================

    queryset = Product.objects.all().prefetch_related(
        'product_images',     # Avoid N+1 query problem
        'color_variants',
        'size_variants'
    )

    # =========================
    # PERMISSIONS
    # =========================

    # Anyone (even not logged in users) can access products
    permission_classes = [AllowAny] 


    # =========================
    # DYNAMIC SERIALIZER
    # =========================

    def get_serializer_class(self):
        """
        This method decides WHICH serializer to use.

        WHY?
        Because:
        - Reading product → simple serializer (ProductSerializer)
        - Creating/updating product → complex serializer (nested handling)

        """

        # If user is creating or updating product
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer

        # Default → read-only serializer
        return ProductSerializer
    

    # =========================
    # CUSTOM ENDPOINT
    # =========================

    @action(detail=True, methods=['get'])    # Q4
    def reviews(self, request, pk=None):
        """
        Custom API endpoint:

        GET /products/{id}/reviews/

        Returns all reviews for a specific product.
        """

        # Get product by UID (not default id)
        product = get_object_or_404(Product, uid=pk)

        # Fetch all reviews related to this product
        # 'reviews' is reverse relation (Product -> ProductReview)
        reviews = product.reviews.all().order_by('-created_at')

        # Convert queryset → JSON
        serializer = ProductReviewSerializer(reviews, many=True)

        # Return response
        return Response(serializer.data)



# ==========================================================
# CATEGORY VIEWSET (READ ONLY)
# ==========================================================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Only allows:
    - GET /categories/
    - GET /categories/{id}/

    NO create/update/delete allowed
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]



# ==========================================================
# COLOR VARIANT VIEWSET (READ ONLY)
# ==========================================================

class ColorVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Used to fetch available colors for products.
    Example: Red, Blue, Black
    """

    queryset = ColorVariant.objects.all()
    serializer_class = ColorVariantSerializer
    permission_classes = [AllowAny]



# ==========================================================
# SIZE VARIANT VIEWSET (READ ONLY)
# ==========================================================

class SizeVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Used to fetch available sizes.
    Example: S, M, L, XL
    """

    queryset = SizeVariant.objects.all()
    serializer_class = SizeVariantSerializer
    permission_classes = [AllowAny]



# ==========================================================
# PRODUCT REVIEW VIEWSET
# ==========================================================

class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    Handles product reviews.

    Features:
    - Only logged-in users can interact
    - Users can create review
    - Users can update/delete ONLY their own reviews
    """

    # Optimize query → fetch related user & product in same query
    queryset = ProductReview.objects.all().select_related('user', 'product')

    serializer_class = ProductReviewSerializer

    # Only authenticated users allowed
    permission_classes = [IsAuthenticated] 


    # =========================
    # CUSTOM CREATE LOGIC
    # =========================

    def perform_create(self, serializer):
        """
        Automatically assign logged-in user to review.

        Instead of user sending:
        {
          "user": 5
        }

        We do:
        user = request.user
        """

        serializer.save(user=self.request.user)


    # =========================
    # QUERYSET FILTERING (SECURITY)
    # =========================

    def get_queryset(self):
        """
        Controls WHICH data user can access.

        IMPORTANT SECURITY LOGIC:
        """

        queryset = super().get_queryset()

        # If user is trying to UPDATE or DELETE
        if self.action in ['update', 'partial_update', 'destroy']:

            # Only allow their OWN reviews
            return queryset.filter(user=self.request.user)

        # For read → allow all reviews
        return queryset