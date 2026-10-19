from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('shipping-policy/', views.shipping_view, name='shipping'),
    path('return-warranty-policy/', views.returns_view, name='returns'),
    path('privacy-policy/', views.privacy_view, name='privacy'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
]
