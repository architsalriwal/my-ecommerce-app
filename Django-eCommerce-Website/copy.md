# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\ecomm\settings.py

"""
Django settings for ecomm project.
"""

import os
from pathlib import Path
from decouple import config
import stripe
from datetime import timedelta # (kept import even though SimpleJWT block removed)

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(**file**).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-change-this')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = []

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = None
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_EMAIL_VERIFICATION = "none"

SITE_ID = 2

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'django.contrib.sites',
'corsheaders',

    'products',
    'accounts',
    'home',
    'cart',
    'base',
    'orders',
    'channels',



    'rest_framework',
    'django_cognito_jwt',
    # 'rest_framework_simplejwt',  # <- not needed anymore for Cognito-only
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_extensions',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django_countries',
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap4',

]

# Celery Configuration

CELERY_BROKER_URL = 'redis://localhost:6379/0' # Message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # Where to store task results
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Channels Configuration

ASGI_APPLICATION = 'Django-eCommerce-Website.asgi.application' # Update this line

CHANNEL_LAYERS = {
"default": {
"BACKEND": "channels_redis.core.RedisChannelLayer",
"CONFIG": {
"hosts": [("localhost", 6379)],
},
},
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'corsheaders.middleware.CorsMiddleware',
'django.middleware.common.CommonMiddleware',
# 'django.middleware.csrf.CsrfViewMiddleware', # you commented it out; leaving as-is per your request
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'ecomm.urls'

TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [TEMPLATE_DIR],
'APP_DIRS': True,
'OPTIONS': {
'context_processors': [
'django.template.context_processors.debug',
'django.template.context_processors.request',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
],
},
},
]

WSGI_APPLICATION = 'ecomm.wsgi.application'

CORS_ALLOWED_ORIGINS = [
"http://localhost:3000",
"http://127.0.0.1:3000",
"http://localhost:8000",
"http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
'http://localhost:3000',
'http://127.0.0.1:3000',
'http://localhost:8000',
'http://127.0.0.1:8000',
]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_DOMAIN = None

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}

AUTH_PASSWORD_VALIDATORS = [
{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
os.path.join(BASE_DIR, "public/static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'public/media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = (
"django.contrib.auth.backends.ModelBackend",
"allauth.account.auth_backends.AuthenticationBackend",
)

# ---------------------------

# AWS Cognito configuration

# ---------------------------

COGNITO_REGION = config("COGNITO_REGION", default="us-east-1")
COGNITO_USER_POOL_ID = config("COGNITO_USER_POOL_ID", default="us-east-1_RQShizp2h")
COGNITO_APP_CLIENT_ID = config("COGNITO_APP_CLIENT_ID", default="4pca6q1su26h9unk3qqeg2o6f7")

REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': [
'accounts.backends.CognitoJWTAuthentication',
],
'DEFAULT_PERMISSION_CLASSES': [
'rest_framework.permissions.IsAuthenticated',
],
'DEFAULT_PARSER_CLASSES': [
'rest_framework.parsers.JSONParser',
'rest_framework.parsers.FormParser',
'rest_framework.parsers.MultiPartParser',
],
}

COGNITO_AWS_REGION = COGNITO_REGION
COGNITO_USER_POOL_ID = COGNITO_USER_POOL_ID
COGNITO_AUDIENCE = [COGNITO_APP_CLIENT_ID]

# (Removed SIMPLE_JWT block entirely — not used with Cognito)

SOCIALACCOUNT_PROVIDERS = {
"google": {
"SCOPE": ["profile", "email"],
"AUTH_PARAMS": {"access_type": "online"}
},
"facebook": {
'METHOD': 'oauth2',
'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
'SCOPE': ['email', 'public_profile'],
'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
'INIT_PARAMS': {'cookie': True},
'FIELDS': [
'id', 'first_name', 'last_name', 'middle_name',
'name', 'name_format', 'picture', 'short_name'
],
'EXCHANGE_TOKEN': True,
'VERIFIED_EMAIL': False,
'VERSION': 'v17.0',
'GRAPH_API_URL': 'https://graph.facebook.com/v17.0',
}
}

SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET', default='')

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_YOUR_STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_YOUR_STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_YOUR_STRIPE_WEBHOOK_SECRET')

stripe.api_key = STRIPE_SECRET_KEY

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
