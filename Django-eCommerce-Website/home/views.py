# C:\Users\archi\Downloads\Django-eCommerce-Website\Django-eCommerce-Website\home\views.py

# Import render function from django.shortcuts to render templates
from django.shortcuts import render
# Import Product and Category models from products app
from products.models import Product, Category
# Import Q object for complex database queries
from django.db.models import Q
# Import send_mail function to send emails
from django.core.mail import send_mail
# Import settings to access project settings
from django.conf import settings
# Import HttpResponseRedirect for redirecting requests
from django.http import HttpResponseRedirect
# Import messages framework for flash messages
from django.contrib import messages
# Import validate_email for email validation
from django.core.validators import validate_email
# Import pagination classes
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.


def index(request):
    # Get all products from database
    query = Product.objects.all()
    # Get all categories from database
    categories = Category.objects.all()
    # Get sort parameter from URL query string
    selected_sort = request.GET.get('sort')
    # Get category parameter from URL query string
    selected_category = request.GET.get('category')

    # Filter products by selected category if one is specified
    if selected_category:
        query = query.filter(category__category_name=selected_category)

    # Apply sorting based on selected sort parameter
    if selected_sort:
        if selected_sort == 'newest':
            query = query.filter(newest_product=True).order_by('category_id')
        elif selected_sort == 'priceAsc':
            query = query.order_by('price')
        elif selected_sort == 'priceDesc':
            query = query.order_by('-price')

    # Get page number from URL query string, default to 1
    page = request.GET.get('page', 1)
    # Create paginator object with 20 items per page
    paginator = Paginator(query, 20)

    products = None

    try:
        # Get requested page of products
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        products = paginator.page(paginator.num_pages)
    except Exception as e:
        # Print any other errors
        print(e)

    # Prepare context data for template
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
    }
    # Render index template with context data
    return render(request, 'home/index.html', context)


def product_search(request):
    # Get search query from URL parameters, default to empty string
    query = request.GET.get('q', '')

    if query:
        # Search products containing query in product name (case insensitive)
        products = Product.objects.filter(Q(product_name__icontains=query) | Q(
            product_name__istartswith=query))
    else:
        # Return empty queryset if no query
        products = Product.objects.none()

    # Prepare context and render search template
    context = {'query': query, 'products': products}
    return render(request, 'home/search.html', context)


def contact(request):
    # Define view function to handle contact form submissions
    try:
        # Start try block to handle potential errors
        if request.method == "POST":
            # Check if request method is POST
            message_name = request.POST.get('message-name')
            # Get first name from POST data
            message_lname = request.POST.get('message-lname') 
            # Get last name from POST data
            message_email = request.POST.get('message-email')
            # Get email address from POST data
            message = request.POST.get('message')
            # Get message content from POST data
            validate_email(message_email)
            # Validate the email address format

            subject = f"Message from {message_name} {message_lname} - {message_email}"
            # Create email subject line with sender details
            email_from = settings.DEFAULT_FROM_EMAIL
            # Get site's default "from" email from settings

            send_mail(
                subject,
                # Use created subject line
                message,
                # Use message content from form
                message_email,
                # Use sender's email as "from" address
                [email_from],
                # Send to site's default email address
                fail_silently=False,
                # Raise exceptions if email fails
            )

            messages.success(
                request, f'Hii, {message_name}! Thank you for your message. We will get back to you soon...')
            # Show success message to user
            return HttpResponseRedirect(request.path_info)
            # Redirect back to same page after successful submission

        return render(request, 'home/contact.html')
        # For GET requests, display empty contact form

    except Exception:
        # Handle any errors that occur
        messages.warning(request, 'Invalid Email Address!')
        # Show warning message for invalid email

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # Redirect back to previous page if error occurs


def about(request):
    # Render about page template
    return render(request, 'home/about.html')


def terms_and_conditions(request):
    # Render terms and conditions template
    return render(request, 'home/terms_and_conditions.html')


def privacy_policy(request):
    # Render privacy policy template
    return render(request, 'home/privacy_policy.html')
