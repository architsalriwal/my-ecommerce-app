# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\api_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views # Make sure api_views has your ViewSets

# Create a router instance
router = DefaultRouter()

# Register your Product-related ViewSets with the router
router.register(r'products', api_views.ProductViewSet, basename='product')      # Q3
router.register(r'categories', api_views.CategoryViewSet, basename='category')
router.register(r'colors', api_views.ColorVariantViewSet, basename='color')
router.register(r'sizes', api_views.SizeVariantViewSet, basename='size')
router.register(r'reviews', api_views.ProductReviewViewSet, basename='review')
# Removed the wishlist registration line
# router.register(r'wishlist', api_views.WishlistViewSet, basename='wishlist')


# The urlpatterns list now includes the router's URLs and any direct paths
urlpatterns = [
    # Include the router's URLs. This will automatically generate URLs
    # for list, retrieve, create, update, and delete operations for registered ViewSets.
    path('', include(router.urls)),  # Q5

    # If you have any specific function-based views or non-ViewSet paths, add them here
]