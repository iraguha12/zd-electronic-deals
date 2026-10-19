from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('orders/', views.orders_list_view, name='orders'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/add/', views.address_add_view, name='address_add'),
    path('addresses/<uuid:address_id>/edit/', views.address_edit_view, name='address_edit'),
    path('addresses/<uuid:address_id>/delete/', views.address_delete_view, name='address_delete'),
    path('profile/', views.profile_edit_view, name='profile_edit'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('delete-account/', views.request_account_deletion_view, name='delete_account'),
]
