# C:\Users\archi\Downloads\Django-eCommerce-Website\Django-eCommerce-Website\products\views.py

import random  # Importing the random module for random sampling
from .forms import ReviewForm  # Importing the ReviewForm for handling product reviews
from django.urls import reverse  # Importing reverse for URL redirection
from django.contrib import messages  # Importing messages to display feedback to users
from accounts.models import Cart, CartItem  # Importing Cart and CartItem models for cart functionality
from django.contrib.auth.decorators import login_required  # Importing login_required to restrict access to authenticated users
from products.models import Product, SizeVariant, ProductReview, Wishlist  # Importing product-related models
from django.shortcuts import render, redirect, get_object_or_404  # Importing shortcuts for rendering and redirecting

# Create your views here.

def get_product(request, slug):  # View function to get a product by its slug
    product = get_object_or_404(Product, slug=slug)  # Fetching the product or returning a 404 if not found
    sorted_size_variants = product.size_variant.all().order_by('size_name')  # Getting and sorting size variants
    related_products = list(product.category.products.filter(parent=None).exclude(uid=product.uid))  # Fetching related products

    # Review product view
    review = None  # Initializing review variable
    if request.user.is_authenticated:  # Checking if the user is logged in
        try:
            review = ProductReview.objects.get(product=product, user=request.user)  # Trying to get the user's review
        except ProductReview.DoesNotExist:  # If no review exists
            review = None  # Set review to None
    
    # Calculate the rating percentage
    rating_percentage = 0  # Initializing rating percentage
    if product.reviews.exists():  # Checking if the product has reviews
        rating_percentage = (product.get_rating() / 5) * 100  # Calculating rating percentage

    # Handle form 
    if request.metsubmissionhod == 'POST' and request.user.is_authenticated:  # Checking if the request is a POST and user is authenticated
        if review:  # If the user has already reviewed the product
            review_form = ReviewForm(request.POST, instance=review)  # Create a form instance with the existing review
        else:  # If no review exists
            review_form = ReviewForm(request.POST)  # Create a new review form

        if review_form.is_valid():  # Checking if the form is valid
            review = review_form.save(commit=False)  # Saving the review instance without committing to the database
            review.product = product  # Assigning the product to the review
            review.user = request.user  # Assigning the user to the review
            review.save()  # Saving the review to the database
            messages.success(request, "Review added successfully!")  # Displaying success message
            return redirect('get_product', slug=slug)  # Redirecting to the product page
    else:
        review_form = ReviewForm()  # Creating a new review form if not a POST request
    
    # Related product view
    if len(related_products) >= 4:  # Checking if there are at least 4 related products
        related_products = random.sample(related_products, 4)  # Randomly selecting 4 related products

    # Wishlist product to fetch, if the same item/product is present or not.
    in_wishlist = False  # Default value for anonymous users
    if request.user.is_authenticated:  # Checking if the user is logged in
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()  # Checking if the product is in the user's wishlist

    context = {  # Preparing context for rendering the template
        'product': product,  # Passing the product object
        'sorted_size_variants': sorted_size_variants,  # Passing sorted size variants
        'related_products': related_products,  # Passing related products
        'review_form': review_form,  # Passing the review form
        'rating_percentage': rating_percentage,  # Passing the rating percentage
        'in_wishlist': in_wishlist,  # Passing wishlist status
    }

    if request.GET.get('size'):  # Checking if a size is selected in the request
        size = request.GET.get('size')  # Getting the selected size
        price = product.get_product_price_by_size(size)  # Fetching the price for the selected size
        context['selected_size'] = size  # Adding selected size to context
        context['updated_price'] = price  # Adding updated price to context

    return render(request, 'product/product.html', context=context)  # Rendering the product template with context


# Add a product to Wishlist
@login_required
def add_to_wishlist(request, uid):  # View function to add a product to the wishlist
    variant = request.GET.get('size')  # Getting the selected size from the request
    if not variant:  # If no size is selected
        messages.error(request, 'Please select a size before adding to the wishlist!')  # Displaying error message
        return redirect(request.META.get('HTTP_REFERER'))  # Redirecting back to the previous page
    
    product = get_object_or_404(Product, uid=uid)  # Fetching the product or returning a 404 if not found
    size_variant = get_object_or_404(SizeVariant, size_name=variant)  # Fetching the size variant or returning a 404 if not found
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product, size_variant=size_variant)  # Getting or creating the wishlist entry

    if created:  # If the wishlist entry was created
        messages.success(request, "Product added to Wishlist!")  # Displaying success message

    return redirect(reverse('wishlist'))  # Redirecting to the wishlist page


# Remove product from wishlist
@login_required
def remove_from_wishlist(request, uid):  # View function to remove a product from the wishlist
    product = get_object_or_404(Product, uid=uid)  # Fetching the product or returning a 404 if not found
    size_variant_name = request.GET.get('size')  # Getting the size variant name from the request
    
    if size_variant_name:  # If a size variant name is provided
        size_variant = get_object_or_404(SizeVariant, size_name=size_variant_name)  # Fetching the size variant or returning a 404 if not found
        Wishlist.objects.filter(user=request.user, product=product, size_variant=size_variant).delete()  # Deleting the wishlist entry
    else:  # If no size variant name is provided
        Wishlist.objects.filter(user=request.user, product=product).delete()  # Deleting all wishlist entries for the product

    messages.success(request, "Product removed from wishlist!")  # Displaying success message
    return redirect(reverse('wishlist'))  # Redirecting to the wishlist page


# Wishlist View
@login_required
def wishlist_view(request):  # View function to display the user's wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user)  # Fetching the user's wishlist items
    return render(request, 'product/wishlist.html',  # Rendering the wishlist template
                  {'wishlist_items': wishlist_items,}  # Passing the wishlist items to the template
                  )


# Move to cart functionality on wishlist page.
def move_to_cart(request, uid):  # View function to move a product from the wishlist to the cart
    product = get_object_or_404(Product, uid=uid)  # Fetching the product or returning a 404 if not found

    # Find the wishlist item with the corresponding size variant
    wishlist = Wishlist.objects.filter(user=request.user, product=product).first()  # Fetching the first wishlist item for the product
    
    if not wishlist:  # If no wishlist item is found
        messages.error(request, "Item not found in wishlist.")  # Displaying error message
        return redirect('wishlist')  # Redirecting to the wishlist page
    
    size_variant = wishlist.size_variant  # Getting the size variant from the wishlist

    # Remove from wishlist
    wishlist.delete()  # Deleting the wishlist entry

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)  # Getting or creating the user's cart

    # Add the product to the cart with the size variant
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, size_variant=size_variant)  # Getting or creating the cart item

    if not created:  # If the cart item already existed
        cart_item.quantity += 1  # Incrementing the quantity
        cart_item.save()  # Saving the updated cart item

    messages.success(request, "Product moved to cart successfully!")  # Displaying success message
    return redirect('cart')  # Redirecting to the cart page