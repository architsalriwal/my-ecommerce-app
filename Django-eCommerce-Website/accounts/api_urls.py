from django.urls import path
from . import api_views

urlpatterns = [
    path('profile/', api_views.UserProfileView.as_view(), name='api_user_profile'),
    path('register/', api_views.register_user, name='api_register'),
]
