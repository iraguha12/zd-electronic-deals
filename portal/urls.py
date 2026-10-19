from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    # Dashboard
    path('', views.portal_dashboard_view, name='dashboard'),

    # Product & Inventory Management
    path('products/', views.portal_products_list_view, name='products_list'),
    path('products/add/', views.portal_product_create_view, name='product_create'),
    path('products/<uuid:product_id>/', views.portal_product_detail_view, name='product_detail'),
    path('products/<uuid:product_id>/edit/', views.portal_product_edit_view, name='product_edit'),
    path('products/<uuid:product_id>/delete/', views.portal_product_delete_view, name='product_delete'),
    path('products/<uuid:product_id>/images/add/', views.portal_product_image_add_view, name='product_image_add'),
    path('images/<uuid:image_id>/delete/', views.portal_product_image_delete_view, name='product_image_delete'),

    # Category Management
    path('categories/', views.portal_categories_list_view, name='categories_list'),
    path('categories/add/', views.portal_category_create_view, name='category_create'),
    path('categories/<int:category_id>/edit/', views.portal_category_edit_view, name='category_edit'),

    # Order Management
    path('orders/', views.portal_orders_list_view, name='orders_list'),
    path('orders/<str:order_number>/', views.portal_order_detail_view, name='order_detail'),

    # Customer Inquiries
    path('inquiries/', views.portal_inquiries_list_view, name='inquiries_list'),
    path('inquiries/<uuid:inquiry_id>/toggle/', views.portal_inquiry_toggle_view, name='inquiry_toggle'),

    # Owner-Only Business Features
    path('setup/', views.portal_owner_setup_view, name='owner_setup'),
    path('settings/', views.portal_site_settings_view, name='site_settings'),
    path('staff/', views.portal_staff_list_view, name='staff_list'),
    path('staff/<uuid:user_id>/edit/', views.portal_user_role_edit_view, name='user_role_edit'),
    path('audit-logs/', views.portal_audit_logs_view, name='audit_logs'),
]
