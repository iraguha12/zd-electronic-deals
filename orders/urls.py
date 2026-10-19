from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/update/<uuid:product_id>/', views.cart_update_view, name='cart_update'),
    path('cart/clear/', views.cart_clear_view, name='cart_clear'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
]
