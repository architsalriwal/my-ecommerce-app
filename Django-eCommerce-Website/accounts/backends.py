# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\accounts\backends.py

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth
import os
from accounts.models import Profile  # Import the Profile model here

User = get_user_model()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred_path = os.path.join(settings.BASE_DIR, 'ecommerce-app-14cdd-firebase-adminsdk-fbsvc-ad8adaa5ea.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Error: Firebase service account file not found.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")

class FirebaseAuthentication(BaseAuthentication):
    """
    A custom authentication backend to validate Firebase ID Tokens.
    """
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        id_token = auth_header.split(" ", 1)[1]

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            
            if not uid or not email:
                raise exceptions.AuthenticationFailed('Invalid token: missing UID or email.')

            with transaction.atomic():
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = User.objects.create_user(email=email, username=email)
                
                # --- FIX: Use get_or_create() to ensure a profile always exists for the user.
                # This is more robust than the previous check.
                profile, created = Profile.objects.get_or_create(user=user)
                
                # Update firebase_uid on the profile if it has changed
                if profile.firebase_uid != uid:
                    profile.firebase_uid = uid
                    profile.save()

            return (user, None)

        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase ID Token.')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {e}')
