# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\home\api_urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import api_views

router = DefaultRouter()
router.register(r'shipping-addresses', api_views.ShippingAddressViewSet, basename='shipping-address')
router.register(r'orders', api_views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/firebase-login/', api_views.firebase_login, name='firebase-login'),
]