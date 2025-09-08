# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order_and_process, name='create_order'),
]
