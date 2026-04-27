# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\home\api_views.py

# ============================================================
# 📁 FILE: home/api_views.py
# PURPOSE:
# This file contains all API endpoints related to:
# - Shipping Address
# - Orders (COD + Stripe)
# - Firebase Login
# - Stripe Webhooks
# ============================================================


# -------------------- IMPORTS --------------------
from rest_framework import serializers
import logging
# Used for logging important events (debugging, tracking flow)

from rest_framework import viewsets, mixins, status
# DRF tools:
# - viewsets → CRUD APIs automatically
# - status → HTTP response codes (200, 400, etc.)

from rest_framework.response import Response
# Used to send API responses

from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
# - action → custom endpoints inside ViewSets
# - api_view → function-based APIs
# - permission_classes → who can access
# - authentication_classes → how user is authenticated

from rest_framework.permissions import IsAuthenticated, AllowAny
# - IsAuthenticated → only logged-in users
# - AllowAny → anyone can access

from rest_framework.authtoken.models import Token
# Token model for DRF token authentication

from django.db import transaction
# Used for atomic DB operations (all succeed or rollback)

from django.shortcuts import get_object_or_404
# Safely fetch object or return 404

from django.conf import settings
# Access project settings (Stripe keys, Firebase path, etc.)

from django.http import HttpResponse
# Used for returning raw HTTP responses (used in webhooks)

from django.views.decorators.csrf import csrf_exempt
# Disable CSRF for webhook endpoint (Stripe doesn't send CSRF token)

from django.contrib.auth import get_user_model
# Get custom User model

import stripe
# Stripe payment integration library

import json
# For parsing JSON payloads (used in webhook)


# -------------------- MODEL IMPORTS --------------------

from .models import ShippingAddress, Order, OrderItem
# Your core models:
# - ShippingAddress → user addresses
# - Order → main order
# - OrderItem → items inside order

from cart.models import Cart
# Cart model (used to convert cart → order)

from products.models import Product
# Product model (used for stock update)


# -------------------- AUTH & SERIALIZER IMPORTS --------------------

from .firebase_auth import validate_firebase_token
# Custom function to validate Firebase token

from accounts.backends import FirebaseAuthentication
# Custom authentication backend (Firebase)

from .serializers import ShippingAddressSerializer, OrderSerializer, OrderCreateSerializer
# Serializers:
# - ShippingAddressSerializer → address CRUD
# - OrderSerializer → read order data
# - OrderCreateSerializer → validate + create order

from rest_framework.authentication import TokenAuthentication
# DRF token-based authentication


# -------------------- LOGGER SETUP --------------------

# Create a logger for this file
# Used like: logger.info(), logger.error(), etc.
logger = logging.getLogger(__name__)


# -------------------- GLOBAL CONFIG --------------------

User = get_user_model()
# Get your custom User model

# Set Stripe secret key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY


# ============================================================
# 🏠 SHIPPING ADDRESS VIEWSET
# Handles:
# - Create Address
# - Update Address
# - Delete Address
# - List User Addresses
# ============================================================

class ShippingAddressViewSet(viewsets.ModelViewSet):

    # Base queryset (ALL addresses in DB)
    # ⚠️ IMPORTANT: This will be filtered later per user
    queryset = ShippingAddress.objects.all()

    # Serializer to convert model ↔ JSON
    serializer_class = ShippingAddressSerializer

    # Authentication methods:
    # - Firebase token
    # - DRF token
    authentication_classes = [FirebaseAuthentication, TokenAuthentication]

    # Only logged-in users can access
    permission_classes = [IsAuthenticated]


    # -------------------- FILTER DATA PER USER --------------------
    def get_queryset(self):

        # Log which user is requesting data
        logger.info(f"ShippingAddressViewSet: Fetching addresses for user: {self.request.user.id}")

        # 🔥 VERY IMPORTANT:
        # Instead of returning ALL addresses,
        # return ONLY addresses belonging to current user
        return self.queryset.filter(user=self.request.user)


    # -------------------- CREATE ADDRESS --------------------
    def perform_create(self, serializer):

        # Log creation attempt
        logger.info(f"ShippingAddressViewSet: Creating new address for user: {self.request.user.id}")

        # Save address and automatically attach current user
        serializer.save(user=self.request.user)

        logger.info("Shipping address created successfully.")


    # -------------------- UPDATE ADDRESS --------------------
    def perform_update(self, serializer):

        # Log update action
        logger.info(f"ShippingAddressViewSet: Updating address {serializer.instance.uid} for user: {self.request.user.id}")

        # Save updated address (ensuring user remains correct)
        serializer.save(user=self.request.user)

        logger.info("Shipping address updated successfully.")


# ============================================================
# 📦 ORDER VIEWSET
# Handles:
# - Fetch Orders
# - Create Order (COD)
# - Create Stripe Payment Intent
# ============================================================

class OrderViewSet(viewsets.ModelViewSet):

    # Base queryset (all orders)
    queryset = Order.objects.all()

    # Serializer for reading order data
    serializer_class = OrderSerializer

    # Authentication
    authentication_classes = [FirebaseAuthentication, TokenAuthentication]

    # Only logged-in users
    permission_classes = [IsAuthenticated]


    # -------------------- FILTER ORDERS PER USER --------------------
    def get_queryset(self):

        logger.info(f"OrderViewSet: Fetching orders for user: {self.request.user.id}")

        # Return only orders of current user
        return self.queryset.filter(user=self.request.user)


    # ============================================================
    # 💳 STRIPE PAYMENT INTENT CREATION API
    # Endpoint:
    # POST /orders/create_payment_intent/
    #
    # Flow:
    # 1. Validate request
    # 2. Create Order (Pending)
    # 3. Create Stripe PaymentIntent
    # 4. Save Stripe details in Order
    # ============================================================

    @action(detail=False, methods=['post'], url_path='create_payment_intent')
    def create_payment_intent(self, request):

        logger.info(f"OrderViewSet: create_payment_intent request started for user {request.user.id}")
        logger.info(f"Request data received: {request.data}")

        # Validate incoming request using serializer
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})

        logger.info("OrderCreateSerializer validation started.")

        # If invalid → automatically throws error
        serializer.is_valid(raise_exception=True)

        logger.info("OrderCreateSerializer validation successful.")

        # Extract validated objects
        cart = serializer.validated_data['cart']
        shipping_address = serializer.validated_data['shipping_address']
        payment_method = serializer.validated_data['payment_method']

        logger.info(f"Validated data - Cart UID: {cart.uid}, Shipping Address UID: {shipping_address.uid}, Payment Method: {payment_method}")

        # Convert total to cents (Stripe requires smallest currency unit)
        total_amount = int(cart.get_cart_total_price_after_coupon() * 100)

        logger.info(f"Calculated total amount: {total_amount} cents")

        # ------------------------------------------------------------
        # ❌ VALIDATION: Ensure this API is used ONLY for Stripe
        # ------------------------------------------------------------
        if payment_method != 'STRIPE':

            # If someone tries COD here → reject
            logger.warning(f"Invalid payment method '{payment_method}' received for Stripe endpoint.")

            return Response(
                {'error': 'This endpoint is for Stripe payments. Use the POST /orders/ endpoint for COD.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # ------------------------------------------------------------
        # 🔥 MAIN STRIPE FLOW (TRY BLOCK)
        # ------------------------------------------------------------
        try:

            # -------------------- STEP 1: CREATE ORDER --------------------
            # Create an Order BEFORE payment is completed
            # WHY?
            # → We need an Order ID to attach to Stripe metadata
            logger.info("Attempting to create a new Order object...")

            order = Order.objects.create(
                user=request.user,                     # Owner of order
                shipping_address=shipping_address,     # Selected address
                total_amount=total_amount / 100,       # Convert cents → dollars
                payment_method='STRIPE',               # Payment type
                status='Pending',                      # Order not processed yet
                payment_status='pending',              # Payment not done yet
                coupon=cart.coupon                    # Apply coupon if exists
            )

            logger.info(f"New Order created with UID: {order.uid}")


            # -------------------- STEP 2: CREATE STRIPE PAYMENT INTENT --------------------
            # This is the core Stripe object that handles payment

            logger.info("Attempting to create Stripe Payment Intent...")

            payment_intent = stripe.PaymentIntent.create(

                # Amount must be in cents
                amount=total_amount,

                # Currency
                currency='usd',

                # Allow Stripe to automatically choose payment methods
                automatic_payment_methods={
                    'enabled': True,
                },

                # Metadata → VERY IMPORTANT
                # Used later in webhook to identify order
                metadata={
                    'order_uid': str(order.uid),
                    'user_id': str(request.user.id),
                    'cart_uid': str(cart.uid),
                }
            )

            logger.info(f"Stripe Payment Intent created with ID: {payment_intent.id}")


            # -------------------- STEP 3: SAVE STRIPE DATA IN ORDER --------------------
            # Store Stripe details in DB so we can track later

            order.stripe_payment_intent_id = payment_intent.id
            order.stripe_client_secret = payment_intent.client_secret

            # Save updated order
            order.save()

            logger.info("Order updated with Stripe payment intent details.")


            # -------------------- STEP 4: SEND CLIENT SECRET TO FRONTEND --------------------
            # Frontend will use this to complete payment via Stripe.js

            return Response({'clientSecret': payment_intent.client_secret})


        # ------------------------------------------------------------
        # ❌ ERROR HANDLING
        # ------------------------------------------------------------
        except Exception as e:

            logger.error(f"An exception occurred during payment intent creation: {e}", exc_info=True)

            # If order was created but something failed → delete it
            if 'order' in locals():
                logger.info(f"Deleting partially created order {order.uid} due to an error.")
                order.delete()

            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ============================================================
    # 🛒 CREATE ORDER (COD FLOW)
    # Endpoint:
    # POST /orders/
    #
    # Used when payment method = COD
    # ============================================================

    def create(self, request, *args, **kwargs):
        logger.info(f"OrderViewSet: create request started for user {request.user.id}")

        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # 1. Save the order to the database
        order = serializer.save()
        logger.info(f"Order created successfully with UID: {order.uid}")

        # 2. THE CORRECT IMPORT: Absolute import from the 'orders' app
        from orders.tasks import process_order_task
        process_order_task.delay(str(order.uid))

        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# 🔔 STRIPE WEBHOOK
# Endpoint (called by Stripe server, NOT frontend):
# POST /stripe/webhook/
#
# Purpose:
# - Confirm payment success
# - Update Order
# - Move Cart → OrderItems
# - Reduce stock
# ============================================================

@csrf_exempt  # Stripe does not send CSRF token
def stripe_webhook(request):

    logger.info("Stripe Webhook received.")

    # Raw request body from Stripe
    payload = request.body

    # Stripe signature (used to verify request authenticity)
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    event = None


    # -------------------- VERIFY STRIPE SIGNATURE --------------------
    try:

        # Verify that request actually came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        logger.info(f"Stripe Webhook event constructed successfully. Type: {event['type']}")

    except ValueError as e:
        # Invalid payload
        logger.error(f"Error decoding Stripe webhook payload: {e}")
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature (possible attack)
        logger.error(f"Stripe webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    # ------------------------------------------------------------
    # 🎯 HANDLE SUCCESSFUL PAYMENT EVENT
    # ------------------------------------------------------------
    if event['type'] == 'payment_intent.succeeded':

        logger.info("Handling payment_intent.succeeded event.")

        # Extract actual payment object from event
        payment_intent = event['data']['object']

        # Retrieve metadata we stored earlier
        order_uid = payment_intent.get('metadata', {}).get('order_uid')
        cart_uid = payment_intent.get('metadata', {}).get('cart_uid')

        logger.info(f"Extracted metadata - Order UID: {order_uid}, Cart UID: {cart_uid}")


        # ❌ If order UID missing → cannot proceed
        if not order_uid:
            logger.warning("Order UID not found in webhook metadata.")
            return HttpResponse(status=400)


        # ------------------------------------------------------------
        # 🔥 ATOMIC TRANSACTION (VERY IMPORTANT)
        # Either ALL DB operations succeed OR NONE
        # ------------------------------------------------------------
        with transaction.atomic():
            try:

                # -------------------- STEP 1: FIND ORDER --------------------
                # Only fetch if payment still pending (avoid duplicate processing)
                order = Order.objects.get(uid=order_uid, payment_status='pending')

                logger.info(f"Found pending order {order.uid}. Updating its status.")


                # -------------------- STEP 2: UPDATE ORDER STATUS --------------------
                order.payment_status = 'succeeded'
                order.status = 'Processing'

                # Save Stripe charge ID
                order.stripe_charge_id = payment_intent.latest_charge

                order.save()

                logger.info("Order status updated to 'succeeded'.")


                # -------------------- STEP 3: GET CART --------------------
                cart = order.cart

                # Only process if cart exists and not already marked paid
                if cart and not cart.is_paid:

                    logger.info(f"Transferring items from cart {cart.uid} to order {order.uid}.")


                    # -------------------- STEP 4: MOVE CART ITEMS → ORDER ITEMS --------------------
                    for cart_item in cart.cart_items.all():

                        logger.info(f"Creating OrderItem for product {cart_item.product.product_name} (quantity: {cart_item.quantity}).")

                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            color_variant=cart_item.color_variant,
                            size_variant=cart_item.size_variant,
                            quantity=cart_item.quantity,

                            # Save price at purchase time
                            price_at_purchase=cart_item.total_price / cart_item.quantity
                        )


                        # -------------------- STEP 5: UPDATE PRODUCT STOCK --------------------
                        product = cart_item.product

                        logger.info(f"Updating stock for product {product.product_name}. Old stock: {product.stock}, New stock: {product.stock - cart_item.quantity}")

                        product.stock -= cart_item.quantity
                        product.save()


                    # -------------------- STEP 6: MARK CART AS PAID --------------------
                    cart.is_paid = True
                    cart.save()

                    logger.info(f"Cart {cart.uid} marked as paid.")

                # -------------------- STEP 7: TRIGGER CELERY BACKGROUND TASK --------------------
                # We import here to avoid circular imports.
                from orders.tasks import process_order_task
                
                # transaction.on_commit ensures Celery only starts AFTER the database has fully saved everything!
                transaction.on_commit(lambda: process_order_task.delay(str(order.uid)))
                logger.info(f"Celery task successfully queued for order {order.uid}.")

            except Order.DoesNotExist:
                # If already processed OR invalid order
                logger.warning(f"Order with UID {order_uid} not found or not in 'pending' status. Ignoring webhook event.")
                pass

    # Always return 200 to Stripe
    return HttpResponse(status=200)


# ============================================================
# 🔐 FIREBASE LOGIN API
# Purpose:
# - Authenticate user via Firebase
# - Create user if not exists
# - Attach anonymous cart to user
# - Return auth token
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can call login
@authentication_classes([])      # No auth required
def firebase_login(request):

    logger.info("firebase_login view function started.")

    # Get Firebase ID token from frontend
    id_token = request.data.get('id_token')

    if not id_token:
        logger.error("ID token was not provided in the request data.")
        return Response({"error": "ID token not provided."}, status=status.HTTP_400_BAD_REQUEST)


    # -------------------- VALIDATE FIREBASE TOKEN --------------------
    logger.info("ID token received. Proceeding to validation.")

    decoded_token = validate_firebase_token(id_token)

    if not decoded_token:
        logger.error("Token validation failed. Returning 401 Unauthorized.")
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)


    # Extract user info
    email = decoded_token.get('email')
    firebase_uid = decoded_token.get('uid')

    logger.info(f"Token decoded. User email: {email}, Firebase UID: {firebase_uid}")


    if not email:
        logger.error("Email not found in decoded token.")
        return Response({"error": "Email not found in token."}, status=status.HTTP_400_BAD_REQUEST)


    # -------------------- FIND OR CREATE USER --------------------
    try:
        user = User.objects.get(email=email)
        logger.info(f"Existing user found: {user.username} (ID: {user.id})")

    except User.DoesNotExist:
        try:
            logger.info(f"User with email {email} not found. Creating a new user.")

            user = User.objects.create_user(
                username=email,
                email=email,
                password=None  # Firebase handles password
            )

            logger.info(f"New user created with email: {email}, ID: {user.id}")

        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            return Response({"error": f"Failed to create user: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ------------------------------------------------------------
    # 🔥 CART MERGING LOGIC (VERY IMPORTANT)
    # Anonymous cart → Logged-in user cart
    # ------------------------------------------------------------
    with transaction.atomic():

        anonymous_cart_uid = request.data.get('cart_uid')

        logger.info(f"Checking for anonymous cart UID in request data: {anonymous_cart_uid}")

        if anonymous_cart_uid:
            try:
                anonymous_cart = Cart.objects.get(uid=anonymous_cart_uid)

                logger.info(f"Anonymous cart found with UID: {anonymous_cart.uid}")

                # If cart has no user → attach it
                if not anonymous_cart.user:

                    logger.info(f"Cart is currently anonymous. Attaching to user {user.username} (ID: {user.id}).")

                    anonymous_cart.user = user
                    anonymous_cart.save()

                    logger.info("Cart successfully attached to user.")

                else:
                    logger.info(f"Cart with UID {anonymous_cart.uid} already belongs to a user (ID: {anonymous_cart.user.id}). Skipping re-assignment.")

            except Cart.DoesNotExist:
                logger.warning(f"Anonymous cart with UID {anonymous_cart_uid} not found. This is expected if the user had no anonymous cart or it was a new cart.")

        else:
            logger.info("No anonymous cart UID provided in the request.")


    # -------------------- GENERATE TOKEN --------------------
    token, created = Token.objects.get_or_create(user=user)

    logger.info(f"Login successful for user: {user.email}. Token created: {created}")

    return Response({
        "message": "Login successful",
        "user_id": user.pk,
        "token": token.key,
    })


# ============================================================
# 🔐 FIREBASE TOKEN VALIDATION FUNCTION
# ============================================================

def validate_firebase_token(id_token):

    """
    Validates the Firebase ID token and returns the decoded user data.
    """

    try:
        logger.debug("Attempting to verify Firebase ID token...")

        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=5)

        logger.debug("Firebase ID token verified successfully.")
        return decoded_token

    except auth.ExpiredIdTokenError:
        logger.warning("Firebase ID token has expired.")
        return None

    except auth.InvalidIdTokenError as e:
        logger.error(f"Firebase token validation failed. Reason: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred during Firebase token validation: {e}", exc_info=True)
        return None


# ============================================================
# 🧠 ORDER CREATE SERIALIZER (CORE BUSINESS LOGIC)
# ============================================================

class OrderCreateSerializer(serializers.Serializer):

    # Input fields from frontend
    cart_uid = serializers.UUIDField(write_only=True, required=True)
    shipping_address_uid = serializers.UUIDField(write_only=True, required=True)
    payment_method = serializers.CharField(write_only=True, required=True)


    # -------------------- VALIDATION --------------------
    def validate(self, data):

        logger.info("OrderCreateSerializer: validate method started.")

        request = self.context.get('request')

        # Ensure user is logged in
        if not request or not request.user.is_authenticated:
            logger.error("Authentication check failed in OrderCreateSerializer.")
            raise serializers.ValidationError("Authentication required to place an order.")


        cart_uid = data.get('cart_uid')
        shipping_address_uid = data.get('shipping_address_uid')
        payment_method = data.get('payment_method')


        logger.info(f"Validating for user: {request.user.username} (ID: {request.user.id})")


        # -------------------- VALIDATE CART --------------------
        try:
            logger.info(f"Attempting to find cart with uid={cart_uid}, user={request.user.id}, is_paid=False")

            cart = Cart.objects.get(uid=cart_uid, user=request.user, is_paid=False)

            if not cart.cart_items.exists():
                logger.warning(f"Cart {cart_uid} found but it is empty.")
                raise serializers.ValidationError({"cart_uid": "Cart is empty."})

            data['cart'] = cart

        except Cart.DoesNotExist:
            logger.error(f"Cart with UID {cart_uid} not found for user {request.user.username} (ID: {request.user.id}) or is already paid.")
            raise serializers.ValidationError({"cart_uid": "Active cart not found for this user."})


        # -------------------- VALIDATE SHIPPING ADDRESS --------------------
        try:
            shipping_address = ShippingAddress.objects.get(uid=shipping_address_uid, user=request.user)
            data['shipping_address'] = shipping_address

        except ShippingAddress.DoesNotExist:
            logger.error(f"Shipping address {shipping_address_uid} not found for user {request.user.id}.")
            raise serializers.ValidationError({"shipping_address_uid": "Shipping address not found or does not belong to user."})


        # -------------------- VALIDATE PAYMENT METHOD --------------------
        valid_payment_methods = ['COD', 'STRIPE']

        payment_method = payment_method.upper()

        if payment_method not in valid_payment_methods:
            logger.error(f"Invalid payment method received: {payment_method}")
            raise serializers.ValidationError(
                {"payment_method": f"Invalid payment method. Choose from: {', '.join(valid_payment_methods)}"}
            )


        # -------------------- VALIDATE STOCK --------------------
        for cart_item in cart.cart_items.all():

            if not cart_item.product:
                logger.error(f"Product not found for cart item {cart_item.uid}.")
                raise serializers.ValidationError(f"Product not found for item {str(cart_item.uid)[:8]}. Please remove this item.")

            if cart_item.product.stock < cart_item.quantity:
                logger.error(f"Insufficient stock for product {cart_item.product.product_name}. Available: {cart_item.product.stock}, Requested: {cart_item.quantity}")
                raise serializers.ValidationError(
                    f"Insufficient stock for {cart_item.product.product_name}."
                )


        data['payment_method'] = payment_method

        logger.info("OrderCreateSerializer: All validations passed.")

        return data