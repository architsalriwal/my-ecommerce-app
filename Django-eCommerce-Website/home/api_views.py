import logging
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import stripe
import json

from .models import ShippingAddress, Order, OrderItem
from cart.models import Cart
from products.models import Product

from .firebase_auth import validate_firebase_token
from accounts.backends import FirebaseAuthentication
from .serializers import ShippingAddressSerializer, OrderSerializer, OrderCreateSerializer
from rest_framework.authentication import TokenAuthentication

# Set up logging for the module
logger = logging.getLogger(__name__)

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    authentication_classes = [FirebaseAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"ShippingAddressViewSet: Fetching addresses for user: {self.request.user.id}")
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        logger.info(f"ShippingAddressViewSet: Creating new address for user: {self.request.user.id}")
        serializer.save(user=self.request.user)
        logger.info("Shipping address created successfully.")

    def perform_update(self, serializer):
        logger.info(f"ShippingAddressViewSet: Updating address {serializer.instance.uid} for user: {self.request.user.id}")
        serializer.save(user=self.request.user)
        logger.info("Shipping address updated successfully.")

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [FirebaseAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"OrderViewSet: Fetching orders for user: {self.request.user.id}")
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='create_payment_intent')
    def create_payment_intent(self, request):
        logger.info(f"OrderViewSet: create_payment_intent request started for user {request.user.id}")
        logger.info(f"Request data received: {request.data}")
        
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        
        logger.info("OrderCreateSerializer validation started.")
        serializer.is_valid(raise_exception=True)
        logger.info("OrderCreateSerializer validation successful.")

        cart = serializer.validated_data['cart']
        shipping_address = serializer.validated_data['shipping_address']
        payment_method = serializer.validated_data['payment_method']
        
        logger.info(f"Validated data - Cart UID: {cart.uid}, Shipping Address UID: {shipping_address.uid}, Payment Method: {payment_method}")
        
        total_amount = int(cart.get_cart_total_price_after_coupon() * 100)
        logger.info(f"Calculated total amount: {total_amount} cents")

        if payment_method != 'STRIPE':
            logger.warning(f"Invalid payment method '{payment_method}' received for Stripe endpoint.")
            return Response(
                {'error': 'This endpoint is for Stripe payments. Use the POST /orders/ endpoint for COD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            logger.info("Attempting to create a new Order object...")
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=total_amount / 100,
                payment_method='STRIPE',
                status='Pending',
                payment_status='pending',
                coupon=cart.coupon
            )
            logger.info(f"New Order created with UID: {order.uid}")

            logger.info("Attempting to create Stripe Payment Intent...")
            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'order_uid': str(order.uid),
                    'user_id': str(request.user.id),
                    'cart_uid': str(cart.uid),
                }
            )
            logger.info(f"Stripe Payment Intent created with ID: {payment_intent.id}")

            order.stripe_payment_intent_id = payment_intent.id
            order.stripe_client_secret = payment_intent.client_secret
            order.save()
            logger.info("Order updated with Stripe payment intent details.")

            return Response({'clientSecret': payment_intent.client_secret})

        except Exception as e:
            logger.error(f"An exception occurred during payment intent creation: {e}", exc_info=True)
            if 'order' in locals():
                logger.info(f"Deleting partially created order {order.uid} due to an error.")
                order.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info(f"OrderViewSet: create request started for user {request.user.id}")
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        logger.info(f"Order created successfully with UID: {order.uid}")
        
        return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

@csrf_exempt
def stripe_webhook(request):
    logger.info("Stripe Webhook received.")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Stripe Webhook event constructed successfully. Type: {event['type']}")
    except ValueError as e:
        logger.error(f"Error decoding Stripe webhook payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        logger.info("Handling payment_intent.succeeded event.")
        payment_intent = event['data']['object']
        order_uid = payment_intent.get('metadata', {}).get('order_uid')
        cart_uid = payment_intent.get('metadata', {}).get('cart_uid')
        logger.info(f"Extracted metadata - Order UID: {order_uid}, Cart UID: {cart_uid}")

        if not order_uid:
            logger.warning("Order UID not found in webhook metadata.")
            return HttpResponse(status=400)

        with transaction.atomic():
            try:
                order = Order.objects.get(uid=order_uid, payment_status='pending')
                logger.info(f"Found pending order {order.uid}. Updating its status.")
                order.payment_status = 'succeeded'
                order.status = 'Processing'
                order.stripe_charge_id = payment_intent.latest_charge
                order.save()
                logger.info("Order status updated to 'succeeded'.")

                cart = order.cart
                if cart and not cart.is_paid:
                    logger.info(f"Transferring items from cart {cart.uid} to order {order.uid}.")
                    for cart_item in cart.cart_items.all():
                        logger.info(f"Creating OrderItem for product {cart_item.product.product_name} (quantity: {cart_item.quantity}).")
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            color_variant=cart_item.color_variant,
                            size_variant=cart_item.size_variant,
                            quantity=cart_item.quantity,
                            price_at_purchase=cart_item.total_price / cart_item.quantity
                        )
                        product = cart_item.product
                        logger.info(f"Updating stock for product {product.product_name}. Old stock: {product.stock}, New stock: {product.stock - cart_item.quantity}")
                        product.stock -= cart_item.quantity
                        product.save()

                    cart.is_paid = True
                    cart.save()
                    logger.info(f"Cart {cart.uid} marked as paid.")
            except Order.DoesNotExist:
                logger.warning(f"Order with UID {order_uid} not found or not in 'pending' status. Ignoring webhook event.")
                pass

    return HttpResponse(status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def firebase_login(request):
    logger.info("firebase_login view function started.")
    id_token = request.data.get('id_token')
    
    if not id_token:
        logger.error("ID token was not provided in the request data.")
        return Response({"error": "ID token not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info("ID token received. Proceeding to validation.")
    decoded_token = validate_firebase_token(id_token)
    
    if not decoded_token:
        logger.error("Token validation failed. Returning 401 Unauthorized.")
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
    
    email = decoded_token.get('email')
    firebase_uid = decoded_token.get('uid')
    logger.info(f"Token decoded. User email: {email}, Firebase UID: {firebase_uid}")

    if not email:
        logger.error("Email not found in decoded token.")
        return Response({"error": "Email not found in token."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        logger.info(f"Existing user found: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        try:
            logger.info(f"User with email {email} not found. Creating a new user.")
            user = User.objects.create_user(
                username=email,
                email=email,
                password=None
            )
            logger.info(f"New user created with email: {email}, ID: {user.id}")
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            return Response({"error": f"Failed to create user: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with transaction.atomic():
        anonymous_cart_uid = request.data.get('cart_uid')
        logger.info(f"Checking for anonymous cart UID in request data: {anonymous_cart_uid}")
        
        if anonymous_cart_uid:
            try:
                anonymous_cart = Cart.objects.get(uid=anonymous_cart_uid)
                logger.info(f"Anonymous cart found with UID: {anonymous_cart.uid}")

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

    token, created = Token.objects.get_or_create(user=user)
    
    logger.info(f"Login successful for user: {user.email}. Token created: {created}")
    return Response({
        "message": "Login successful",
        "user_id": user.pk,
        "token": token.key,
    })

import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

print("DEBUG: Django server is starting up and loading firebase_auth.py")

if not firebase_admin._apps:
    try:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        logger.info(f"Attempting to initialize Firebase Admin SDK from: {cred_path}")
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        else:
            logger.error(f"Firebase service account file not found at {cred_path}")
            
    except Exception as e:
        logger.critical(f"FATAL ERROR: Failed to initialize Firebase Admin SDK: {e}", exc_info=True)

def validate_firebase_token(id_token):
    """
    Validates the Firebase ID token and returns the decoded user data.
    """
    try:
        logger.debug("Attempting to verify Firebase ID token...")
        decoded_token = auth.verify_id_token(id_token)
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

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import ShippingAddress, Order, OrderItem
from cart.models import Cart
from products.models import Product, ColorVariant, SizeVariant, Coupon
from products.serializers import CouponSerializer

User = get_user_model()

class ShippingAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShippingAddress
        fields = [
            'uid', 'user', 'full_name', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'phone_number',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    color_name = serializers.CharField(source='color_variant.color_name', read_only=True, allow_null=True)
    size_name = serializers.CharField(source='size_variant.size_name', read_only=True, allow_null=True)

    class Meta:
        model = OrderItem
        fields = [
            'uid', 'product_name', 'color_name', 'size_name', 'quantity', 'price_at_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    shipping_address_detail = ShippingAddressSerializer(source='shipping_address', read_only=True)
    coupon_detail = CouponSerializer(source='coupon', read_only=True)

    class Meta:
        model = Order
        fields = [
            'uid', 'user', 'user_username', 'shipping_address', 'shipping_address_detail',
            'total_amount', 'payment_method', 'status', 'payment_status', 'order_items', 'coupon', 'coupon_detail',
            'created_at', 'updated_at', 'stripe_payment_intent_id', 'stripe_client_secret', 'stripe_charge_id'
        ]
        read_only_fields = [
            'uid', 'user', 'user_username', 'shipping_address', 'shipping_address_detail',
            'total_amount', 'payment_method', 'status', 'payment_status', 'order_items',
            'coupon', 'coupon_detail', 'created_at', 'updated_at',
            'stripe_payment_intent_id', 'stripe_client_secret', 'stripe_charge_id'
        ]

class OrderCreateSerializer(serializers.Serializer):
    cart_uid = serializers.UUIDField(write_only=True, required=True)
    shipping_address_uid = serializers.UUIDField(write_only=True, required=True)
    payment_method = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        logger.info("OrderCreateSerializer: validate method started.")
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            logger.error("Authentication check failed in OrderCreateSerializer.")
            raise serializers.ValidationError("Authentication required to place an order.")
        
        cart_uid = data.get('cart_uid')
        shipping_address_uid = data.get('shipping_address_uid')
        payment_method = data.get('payment_method')
        
        logger.info(f"Validating for user: {request.user.username} (ID: {request.user.id})")
        logger.info(f"Received cart_uid: {cart_uid}, shipping_address_uid: {shipping_address_uid}, payment_method: {payment_method}")
        
        try:
            # THIS IS THE CRITICAL QUERY
            logger.info(f"Attempting to find cart with uid={cart_uid}, user={request.user.id}, is_paid=False")
            cart = Cart.objects.get(uid=cart_uid, user=request.user, is_paid=False)
            if not cart.cart_items.exists():
                logger.warning(f"Cart {cart_uid} found but it is empty.")
                raise serializers.ValidationError({"cart_uid": "Cart is empty."})
            data['cart'] = cart
            logger.info(f"Successfully found and validated cart {cart_uid} for user {request.user.id}")
        except Cart.DoesNotExist:
            logger.error(f"Cart with UID {cart_uid} not found for user {request.user.username} (ID: {request.user.id}) or is already paid.")
            raise serializers.ValidationError({"cart_uid": "Active cart not found for this user."})
        
        try:
            shipping_address = ShippingAddress.objects.get(uid=shipping_address_uid, user=request.user)
            data['shipping_address'] = shipping_address
            logger.info(f"Successfully validated shipping address {shipping_address_uid} for user {request.user.id}")
        except ShippingAddress.DoesNotExist:
            logger.error(f"Shipping address {shipping_address_uid} not found for user {request.user.id}.")
            raise serializers.ValidationError({"shipping_address_uid": "Shipping address not found or does not belong to user."})
        
        valid_payment_methods = ['COD', 'STRIPE']
        payment_method = payment_method.upper()
        if payment_method not in valid_payment_methods:
            logger.error(f"Invalid payment method received: {payment_method}")
            raise serializers.ValidationError(
                {"payment_method": f"Invalid payment method. Choose from: {', '.join(valid_payment_methods)}"}
            )
        
        for cart_item in cart.cart_items.all():
            if not cart_item.product:
                logger.error(f"Product not found for cart item {cart_item.uid}.")
                raise serializers.ValidationError(f"Product not found for item {str(cart_item.uid)[:8]}. Please remove this item.")
            if cart_item.product.stock < cart_item.quantity:
                logger.error(f"Insufficient stock for product {cart_item.product.product_name}. Available: {cart_item.product.stock}, Requested: {cart_item.quantity}")
                raise serializers.ValidationError(
                    f"Insufficient stock for {cart_item.product.product_name}. Available: {cart_item.product.stock}, Requested: {cart_item.quantity}"
                )

        data['payment_method'] = payment_method
        logger.info("OrderCreateSerializer: All validations passed.")
        return data

    def create(self, validated_data):
        logger.info("OrderCreateSerializer: create method started (for COD).")
        user = self.context['request'].user
        cart = validated_data.pop('cart')
        shipping_address = validated_data.pop('shipping_address')
        payment_method = validated_data.pop('payment_method')

        if payment_method != 'COD':
            logger.error(f"Invalid call to create method for payment method '{payment_method}'. Should only be used for COD.")
            raise serializers.ValidationError("This serializer's create method is for COD payments only.")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                cart=cart,
                shipping_address=shipping_address,
                total_amount=cart.get_cart_total_price_after_coupon(),
                payment_method=payment_method,
                status='Processing',
                payment_status='succeeded',
                coupon=cart.coupon
            )
            logger.info(f"New Order created (COD) with UID: {order.uid}.")

            for cart_item in cart.cart_items.all():
                logger.info(f"Creating OrderItem for product {cart_item.product.product_name}...")
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    color_variant=cart_item.color_variant,
                    size_variant=cart_item.size_variant,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.total_price / cart_item.quantity
                )
                product = cart_item.product
                logger.info(f"Updating stock for {product.product_name}. New stock: {product.stock - cart_item.quantity}")
                product.stock -= cart_item.quantity
                product.save()

            cart.is_paid = True
            cart.save()
            logger.info(f"Cart {cart.uid} marked as paid for COD order.")
            
            return order
