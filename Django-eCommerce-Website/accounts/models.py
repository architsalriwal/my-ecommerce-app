# C:\Users\archi\Downloads\Django-eCommerce-Website\accounts\models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel 

# This is the custom User model that your settings.py file refers to.
# By inheriting from AbstractUser, we get all of Django's built-in
# authentication features (username, email, password, etc.).
class User(AbstractUser):
    pass

class Profile(BaseModel):
    # We link the Profile to our new custom User model defined above.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True, help_text="The unique ID from Firebase Authentication")

    def __str__(self):
        return f"Profile of {self.user.username}"