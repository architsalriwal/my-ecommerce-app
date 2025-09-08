# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\cart\urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter # <-- IMPORTANT CHANGE: Use SimpleRouter
from . import api_views

# Use a SimpleRouter for CartItemViewSet. SimpleRouter is less aggressive
# about generating an APIRootView at its base path when included.
cart_item_router = SimpleRouter() # <-- Changed to SimpleRouter
cart_item_router.register(r'items', api_views.CartItemViewSet, basename='cart-item')

urlpatterns = [
    # 1. FIRST: Explicitly define the GET route for the root /api/cart/
    # This must still come before the router's inclusion to ensure precedence.
    path('', api_views.CartViewSet.as_view({'get': 'retrieve'}), name='cart-detail'),

    # 2. THEN: Include the CartItemViewSet URLs from the SimpleRouter.
    # This should now ONLY create /api/cart/items/ and /api/cart/items/<uid>/ paths,
    # without creating a conflicting APIRootView at /api/cart/.
    path('', include(cart_item_router.urls)),

    # 3. Finally: Explicitly define routes for custom actions on the CartViewSet
    path('apply-coupon/', api_views.CartViewSet.as_view({'post': 'apply_coupon'}), name='cart-apply-coupon'),
    path('remove-coupon/', api_views.CartViewSet.as_view({'post': 'remove_coupon'}), name='cart-remove-coupon'),
]

# IMPORTANT: There should be NO other router.register(r'', api_views.CartViewSet, ...) line in this file.