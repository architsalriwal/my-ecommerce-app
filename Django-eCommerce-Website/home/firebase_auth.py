import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

# TEST: This message should appear in your terminal when you start the server.
print("DEBUG: Django server is starting up and loading firebase_auth.py")

# Initialize the Firebase Admin SDK once when the app starts.
if not firebase_admin._apps:
    try:
        # Use the path from settings.py for the credentials file
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        
        # Add logging to confirm the file path is being read correctly
        print(f"DEBUG: Attempting to initialize Firebase Admin SDK from: {cred_path}")
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("DEBUG: Firebase Admin SDK initialized successfully.")
        else:
            print(f"ERROR: Firebase service account file not found at {cred_path}")
            
    except Exception as e:
        print(f"FATAL ERROR: Failed to initialize Firebase Admin SDK: {e}")

def validate_firebase_token(id_token):
    """
    Validates the Firebase ID token and returns the decoded user data.
    """
    try:
        # The verify_id_token method handles all the validation and decoding.
        print("DEBUG: Attempting to verify Firebase ID token...")
        decoded_token = auth.verify_id_token(id_token)
        print("DEBUG: Firebase ID token verified successfully.")
        return decoded_token
    except auth.ExpiredIdTokenError:
        print("ERROR: Firebase ID token has expired.")
        return None
    except auth.InvalidIdTokenError as e:
        # This will print the precise reason the token is invalid
        print(f"ERROR: Firebase token validation failed. Reason: {e}")
        return None
    except Exception as e:
        # Catch other, less common errors
        print(f"ERROR: An unexpected error occurred during Firebase token validation: {e}")
        return None
