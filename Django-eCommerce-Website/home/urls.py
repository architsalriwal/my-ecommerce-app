# C:\Users\archi\Downloads\Django-eCommerce-Website\Django-eCommerce-Website\home\urls.py


from django.urls import path
from home.views import *

urlpatterns = [
    path('', index , name= 'home'),
    path('search/', product_search, name='product_search'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('terms-and-conditions/', terms_and_conditions, name='terms-and-conditions'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),

]
