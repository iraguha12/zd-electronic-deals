from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
]
