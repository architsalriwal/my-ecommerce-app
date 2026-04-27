import pytest
from unittest.mock import patch
from django.test import Client
from django.urls import reverse
from home.models import Order
from home.tests.factories import UserFactory, CartFactory, ShippingAddressFactory

@pytest.mark.django_db
class TestStripeWebhook:
    
    def setup_method(self):
        """Set up dynamic dummy data using factory_boy"""
        self.client = Client()
        self.user = UserFactory()
        self.cart = CartFactory(user=self.user)
        self.shipping_address = ShippingAddressFactory(user=self.user)
        
        # Create a pending order, just like the real DB would have
        self.order = Order.objects.create(
            user=self.user,
            cart=self.cart,
            shipping_address=self.shipping_address,
            total_amount=100.00,
            payment_method='STRIPE',
            status='Pending',
            payment_status='pending'
        )

    # THIS IS THE INTERVIEW STORY: We are mocking the Stripe SDK!
    @patch('home.api_views.stripe.Webhook.construct_event')
    def test_stripe_payment_succeeded_webhook(self, mock_construct_event):
        """
        Test that a valid Stripe webhook correctly updates the Order status
        and triggers the atomic database transaction without hitting the network.
        """
        # 1. Define what the mock should return (A simulated Stripe JSON payload)
        mock_construct_event.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'metadata': {
                        'order_uid': str(self.order.uid),
                        'cart_uid': str(self.cart.uid)
                    },
                    'latest_charge': 'ch_mock_12345'
                }
            }
        }

        # 2. Dynamically resolve the URL so it won't break if routing changes
        webhook_url = reverse('stripe_webhook')

        # 3. Simulate Stripe sending an HTTP POST request to our webhook URL
        # We send garbage data ('{}') because the mock bypasses the signature check anyway!
        response = self.client.post(
            webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='mock_signature'
        )

        # 4. Assert the HTTP response was successful
        assert response.status_code == 200

        # 5. Assert our Django Business Logic executed correctly!
        self.order.refresh_from_db()
        assert self.order.payment_status == 'succeeded'
        assert self.order.status == 'Processing'
        assert self.order.stripe_charge_id == 'ch_mock_12345'
        
        self.cart.refresh_from_db()
        assert self.cart.is_paid == True