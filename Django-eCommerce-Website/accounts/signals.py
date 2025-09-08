# C:\Users\archi\Downloads\Django-eCommerce-Website\accounts\signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Profile


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)  # We removed this earlier


# @receiver(post_save, sender=User)  # Remove this entire signal handler
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()