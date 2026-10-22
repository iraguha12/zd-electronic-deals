"""
Main URL Configuration for zd_electronics.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Business Management Portal (Owner & Operations Staff)
    path('portal/', include('portal.urls', namespace='portal')),
    
    # Customer Accounts & Auth
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    # Product Catalogue & Search
    path('products/', include('catalog.urls', namespace='catalog')),
    
    # Shopping Cart, Order Requests & Quotes
    path('orders/', include('orders.urls', namespace='orders')),
    
    # Standard Django Admin (Secondary fallback)
    path('admin/', admin.site.urls),
    
    # Marketing, Policies, Sourcing & Contact Pages (Root)
    path('', include('pages.urls', namespace='pages')),
]

from django.urls import re_path
from django.views.static import serve

# Unconditionally serve uploaded media files (photos, videos) in development and production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
