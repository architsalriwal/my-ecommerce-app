# C:\Users\archi\Downloads\Django-eCommerce-Website\ecomm\api_urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from products import api_views as products_api_views
from accounts import api_urls as accounts_api_urls
from cart import urls as cart_api_urls
from home import api_urls as home_api_urls

router = DefaultRouter()

# Register Products App ViewSets
router.register(r'products', products_api_views.ProductViewSet, basename='product')
router.register(r'categories', products_api_views.CategoryViewSet, basename='category')
router.register(r'colors', products_api_views.ColorVariantViewSet, basename='color-variant')
router.register(r'sizes', products_api_views.SizeVariantViewSet, basename='size-variant')
router.register(r'reviews', products_api_views.ProductReviewViewSet, basename='product-review')
router.register(r'wishlist', products_api_views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)), 
    path('auth/', include(accounts_api_urls)),
    path('cart/', include(cart_api_urls)),
    path('home/', include(home_api_urls)),
]

