import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from home.tests.factories import UserFactory, CartFactory, CartItemFactory

@pytest.mark.django_db
class TestFirebaseAuthAndCartMerge:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(email="test@mergecart.com")
        self.anonymous_cart = CartFactory(user=None, session_key="anon_session_123")
        self.cart_item = CartItemFactory(cart=self.anonymous_cart, quantity=2)

    @patch('home.api_views.validate_firebase_token')
    def test_firebase_login_merges_anonymous_cart(self, mock_validate_token):
        """
        Tests the complex state transition: assigning an anonymous cart 
        to an authenticated user upon a successful Firebase login.
        """
        # 1. Mock the Firebase SDK response
        mock_validate_token.return_value = {
            'uid': 'firebase_mock_uid_123',
            'email': self.user.email 
        }

        # 2. Simulate the frontend payload containing the anonymous cart UID
        payload = {
            'id_token': 'mock.jwt.token',
            'cart_uid': str(self.anonymous_cart.uid)
        }

        # 3. Hit the resolved URL from your routing configuration
        response = self.client.post(
            '/api/home/auth/firebase-login/',
            data=payload,
            format='json'
        )

        # 4. Assert Success
        assert response.status_code == 200
        assert 'token' in response.data

        # 5. Assert Database State Transition (The Senior assertion)
        self.anonymous_cart.refresh_from_db()
        assert self.anonymous_cart.user == self.user
        assert self.anonymous_cart.cart_items.count() == 1