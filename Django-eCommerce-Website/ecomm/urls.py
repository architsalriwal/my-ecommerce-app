from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.decorators.csrf import csrf_exempt 
from django.middleware.csrf import get_token
from django.http import JsonResponse

from products import api_urls as products_api_urls
from accounts import api_urls as accounts_api_urls
from cart import urls as cart_api_urls
from home import api_urls as home_api_urls
from home import api_views as home_api_views


def get_csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path("accounts/", include("allauth.urls")),
    
    path('api/', include([
        path('products/', include(products_api_urls)),
        path('auth/', include(accounts_api_urls)),
        path('cart/', include(cart_api_urls)),
        path('home/', include(home_api_urls)),
        path('auth/csrf-token/', get_csrf_token_view, name='csrf-token'),
        path('stripe/webhook/', csrf_exempt(home_api_views.stripe_webhook), name='stripe_webhook'),
    ])),
]


# ✅ DEBUG TOOLBAR CONFIG
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)