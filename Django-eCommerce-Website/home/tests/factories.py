import factory
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Cart, CartItem
from home.models import Order, ShippingAddress

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

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
    
    is_paid = False

class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1

class ShippingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingAddress
        
    user = factory.SubFactory(UserFactory)
    full_name = factory.Faker('name')
    address_line1 = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    postal_code = factory.Faker('zipcode')
    country = "USA"