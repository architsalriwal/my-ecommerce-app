# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\accounts\tests\test_auth.py
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import UserFactory, CartFactory, CartItemFactory

@pytest.mark.django_db
class TestFirebaseAuthAndCartMerge:
    
    def setup_method(self):
        self.client = APIClient()
        # 1. Generate a User using our new Factory
        self.user = UserFactory(email="test@mergcart.com")
        
        # 2. Generate an "Anonymous" Cart (No user attached)
        self.anonymous_cart = CartFactory(user=None, session_key="anon_session_123")
        
        # 3. Add an item to the anonymous cart
        self.cart_item = CartItemFactory(cart=self.anonymous_cart, quantity=2)

    # Mock the Firebase Admin SDK so we don't actually hit Google's servers
    @patch('home.api_views.validate_firebase_token')
    def test_firebase_login_merges_anonymous_cart(self, mock_validate_token):
        """
        Tests that an anonymous cart is successfully transferred to the 
        authenticated user upon a successful Firebase login.
        """
        # 1. Define what the mocked Firebase token should return
        mock_validate_token.return_value = {
            'uid': 'firebase_mock_uid_123',
            'email': self.user.email  # Matches the user we created in setup
        }

        # 2. Simulate the React frontend sending the ID token AND the anonymous cart UID
        payload = {
            'id_token': 'mock.jwt.token',
            'cart_uid': str(self.anonymous_cart.uid)
        }

        # 3. Hit the login endpoint
        response = self.client.post(
            '/api/auth/firebase_login/', # Replace with your actual URL route
            data=payload,
            format='json'
        )

        # 4. Assert the HTTP response was successful
        assert response.status_code == 200
        assert 'token' in response.data

        # 5. THE CRITICAL ASSERTION: Did the database state transition work?
        self.anonymous_cart.refresh_from_db()
        
        # Prove the cart is no longer anonymous, and now belongs to the User!
        assert self.anonymous_cart.user == self.user
        assert self.anonymous_cart.cart_items.count() == 1
        assert self.anonymous_cart.cart_items.first().quantity == 2