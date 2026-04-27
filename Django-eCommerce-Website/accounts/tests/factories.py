# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\accounts\tests\factories.py

import factory
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Cart, CartItem

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # Dynamically generate unique emails and usernames using Faker
    username = factory.Faker('user_name')
    email = factory.Faker('email')

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    category_name = factory.Faker('word')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    product_name = factory.Faker('catch_phrase')
    category = factory.SubFactory(CategoryFactory)
    price = 25.00
    stock = 100

class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart
    
    # By default, we leave user and session_key blank to customize in the test
    is_paid = False

class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1