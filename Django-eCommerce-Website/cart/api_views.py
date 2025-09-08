from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import Http404
from django.db.models import F

from .models import Cart, CartItem
from products.models import Product, ColorVariant, SizeVariant, Coupon
from home.models import ShippingAddress
from orders.models import Order 
from orders.tasks import process_order_task 
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemCreateUpdateSerializer, ApplyCouponSerializer
)
from products.serializers import ProductSerializer, ColorVariantSerializer, SizeVariantSerializer


# --- Utility Function for Cart Retrieval and Merging ---
# This is the new, robust function to get the correct cart for the request.
def get_cart_for_user_or_session(request):
    """
    Retrieves or creates an active cart. If an anonymous user with a cart logs in,
    this function merges their anonymous cart into their user-specific cart.
    """
    user = request.user
    session_key = request.session.session_key
    
    # Check for an active user cart first
    user_cart = None
    if user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        if created:
            print(f"New user cart created for {user.username}.")
    
    # Check for an active anonymous cart
    anonymous_cart = None
    if session_key:
        try:
            anonymous_cart = Cart.objects.get(session_key=session_key, is_paid=False)
        except Cart.DoesNotExist:
            pass

    # MERGING LOGIC: If both a user cart and an anonymous cart exist, merge them
    if user.is_authenticated and anonymous_cart and user_cart:
        print(f"Merging anonymous cart {anonymous_cart.uid} into user cart {user_cart.uid}.")
        with transaction.atomic():
            # Iterate through anonymous cart items
            for anon_item in anonymous_cart.cart_items.all():
                # Check if the item already exists in the user's cart
                existing_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=anon_item.product,
                    color_variant=anon_item.color_variant,
                    size_variant=anon_item.size_variant,
                    defaults={'quantity': anon_item.quantity}
                )
                
                # If the item existed, just update the quantity
                if not created:
                    existing_item.quantity = F('quantity') + anon_item.quantity
                    existing_item.save()
            
            # Delete the now-empty anonymous cart
            anonymous_cart.delete()
            print("Anonymous cart deleted after merge.")
        
        return user_cart
    
    # If the user is authenticated and they have a cart (either new or existing)
    if user_cart:
        return user_cart
    
    # If the user is authenticated but had no cart, and there was no anonymous cart
    if user.is_authenticated:
        return user_cart or Cart.objects.create(user=user)
        
    # If the user is anonymous, just return the anonymous cart (create if needed)
    if session_key:
        return anonymous_cart or Cart.objects.get_or_create(session_key=session_key, is_paid=False)[0]

    # As a fallback, create a new anonymous cart if all else fails
    request.session.create()
    return Cart.objects.create(session_key=request.session.session_key)


# --- Re-written ViewSets to use the new utility function ---
class CartViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ["apply_coupon_to_cart", "remove_coupon_from_cart", "checkout"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_object(self):
        # Now, this method is simple: just call the shared utility
        return get_cart_for_user_or_session(self.request)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response([serializer.data]) 

    @action(detail=False, methods=['post'], url_path='apply-coupon')
    def apply_coupon_to_cart(self, request):
        cart = self.get_object()
        serializer = ApplyCouponSerializer(data=request.data, context={'request': request, 'cart': cart})
        serializer.is_valid(raise_exception=True)
        coupon_code = serializer.validated_data['coupon_code']

        try:
            coupon = get_object_or_404(Coupon, coupon_code=coupon_code, is_active=True)

            if cart.coupon == coupon:
                return Response({"detail": "Coupon already applied."}, status=status.HTTP_400_BAD_REQUEST)

            if cart.get_cart_total() < coupon.minimum_amount:
                return Response(
                    {"detail": f"Cart total must be at least ${coupon.minimum_amount:.2f} to apply this coupon."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart.coupon = coupon
            cart.save()
            updated_cart_serializer = CartSerializer(cart)
            return Response({"message": "Coupon applied successfully!", "cart": updated_cart_serializer.data},
                             status=status.HTTP_200_OK)
        except Http404:
            return Response({"detail": "Invalid or expired coupon code."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='remove-coupon')
    def remove_coupon_from_cart(self, request):
        cart = self.get_object()
        if not cart.coupon:
            return Response({"detail": "No coupon is currently applied to the cart."},
                             status=status.HTTP_400_BAD_REQUEST)

        cart.coupon = None
        cart.save()
        updated_cart_serializer = CartSerializer(cart)
        return Response({"message": "Coupon removed successfully!", "cart": updated_cart_serializer.data},
                         status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        with transaction.atomic():
            cart = self.get_object()

            if not cart.cart_items.exists():
                return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=request.user, 
                total_amount=cart.get_final_total()
            )

            for cart_item in cart.cart_items.all():
                cart_item.order = order
                cart_item.cart = None 
                cart_item.save()

            cart.coupon = None
            cart.is_paid = True
            cart.save()

        process_order_task.delay(str(order.uid)) 

        return Response({
            "message": "Order placed successfully! Redirecting to status page...",
            "order_uid": str(order.uid)
        }, status=status.HTTP_202_ACCEPTED) 


class CartItemViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CartItemCreateUpdateSerializer
    permission_classes = [AllowAny] 

    def get_current_cart(self):
        # Now uses the shared utility function
        return get_cart_for_user_or_session(self.request)

    def get_queryset(self):
        return CartItem.objects.filter(cart=self.get_current_cart())

    def get_object(self):
        cart_item_uid = self.kwargs.get('pk')
        if not cart_item_uid:
            raise Http404("Cart item UID not provided.")
        return get_object_or_404(self.get_queryset(), uid=cart_item_uid)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart'] = self.get_current_cart()
        return context

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        cart = self.get_current_cart()
        return Response(CartSerializer(cart, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        cart = self.get_current_cart()
        return Response(CartSerializer(cart, context={'request': request}).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        cart = self.get_current_cart()
        return Response(CartSerializer(cart, context={'request': request}).data, status=status.HTTP_200_OK)
