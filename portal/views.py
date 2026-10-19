from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q, F
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from accounts.models import CustomUser
from accounts.permissions import staff_member_required, manager_required, owner_required
from catalog.models import Product, ProductImage, Category
from orders.models import Order, OrderItem
from pages.models import ContactMessage
from portal.models import SiteSettings, AuditLog
from portal.forms import (
    ProductForm, ProductImageForm, CategoryForm,
    OrderStatusUpdateForm, SiteSettingsForm, StaffRoleUpdateForm
)


def log_activity(user, action, details="", ip=""):
    """Helper to record audit logs for critical operations"""
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details,
        ip_address=ip
    )


@staff_member_required
def portal_dashboard_view(request):
    """
    Central operations dashboard:
    - Order metrics and status breakdowns
    - Low-stock inventory alerts
    - Financial & Profit summary (OWNER ONLY)
    """
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status=Order.STATUS_PENDING).count()
    sourcing_orders = Order.objects.filter(status=Order.STATUS_SOURCING).count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold'), is_published=True)
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:8]
    unread_inquiries = ContactMessage.objects.filter(is_resolved=False).count()

    total_revenue = Decimal('0.00')
    total_profit = Decimal('0.00')

    # Financial estimates calculated strictly for Owner
    if request.user.is_owner:
        completed_orders = Order.objects.filter(status__in=[Order.STATUS_DELIVERED, Order.STATUS_CONFIRMED, Order.STATUS_OUT_DELIVERY])
        revenue_agg = completed_orders.aggregate(total=Sum('total_amount'))
        total_revenue = revenue_agg['total'] or Decimal('0.00')
        
        # Calculate profit across all delivered/active order items:
        for order in completed_orders.prefetch_related('items'):
            total_profit += order.total_order_profit

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'sourcing_orders': sourcing_orders,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products[:6],
        'recent_orders': recent_orders,
        'unread_inquiries': unread_inquiries,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'is_owner': request.user.is_owner,
    }
    return render(request, 'portal/dashboard.html', context)


# --- PRODUCT & INVENTORY MANAGEMENT ---

@manager_required
def portal_products_list_view(request):
    """View and filter all products in inventory."""
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    products = Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all().order_by('name')
    return render(request, 'portal/products_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
    })


@manager_required
def portal_product_create_view(request):
    """Add a new product to catalogue."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            log_activity(request.user, "PRODUCT_CREATED", f"Created product {product.name} ({product.sku})")
            messages.success(request, f"Product '{product.name}' was added successfully.")
            return redirect('portal:product_detail', product_id=product.id)
    else:
        form = ProductForm()

    return render(request, 'portal/product_form.html', {'form': form, 'title': 'Add New Electronics Product'})


@manager_required
def portal_product_edit_view(request, product_id):
    """Edit existing product details, prices, specifications, and stock."""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            log_activity(request.user, "PRODUCT_UPDATED", f"Updated product {product.name} ({product.sku})")
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('portal:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'portal/product_form.html', {'form': form, 'product': product, 'title': f'Edit {product.name}'})


@manager_required
def portal_product_detail_view(request, product_id):
    """Portal detail view for a product including its image gallery management."""
    product = get_object_or_404(Product.objects.prefetch_related('images'), id=product_id)
    image_form = ProductImageForm()
    return render(request, 'portal/product_detail.html', {
        'product': product,
        'image_form': image_form,
    })


@manager_required
@require_POST
def portal_product_image_add_view(request, product_id):
    """Upload or attach an image to a product."""
    product = get_object_or_404(Product, id=product_id)
    form = ProductImageForm(request.POST, request.FILES)
    if form.is_valid():
        img = form.save(commit=False)
        img.product = product
        img.save()
        messages.success(request, "Product image added successfully.")
    else:
        messages.error(request, "Failed to upload image. Please check the file.")
    return redirect('portal:product_detail', product_id=product.id)


@manager_required
@require_POST
def portal_product_image_delete_view(request, image_id):
    """Remove a product image."""
    img = get_object_or_404(ProductImage, id=image_id)
    product_id = img.product.id
    img.delete()
    messages.success(request, "Image removed.")
    return redirect('portal:product_detail', product_id=product_id)


@manager_required
@require_POST
def portal_product_delete_view(request, product_id):
    """Delete a product from the database."""
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    sku = product.sku
    product.delete()
    log_activity(request.user, "PRODUCT_DELETED", f"Deleted product {name} ({sku})")
    messages.success(request, f"Product '{name}' was deleted.")
    return redirect('portal:products_list')


# --- CATEGORY MANAGEMENT ---

@manager_required
def portal_categories_list_view(request):
    """Manage categories."""
    categories = Category.objects.all().order_by('display_order', 'name')
    return render(request, 'portal/categories_list.html', {'categories': categories})


@manager_required
def portal_category_create_view(request):
    """Create a new product category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            log_activity(request.user, "CATEGORY_CREATED", f"Created category {category.name}")
            messages.success(request, f"Category '{category.name}' created.")
            return redirect('portal:categories_list')
    else:
        form = CategoryForm()
    return render(request, 'portal/category_form.html', {'form': form, 'title': 'Create Product Category'})


@manager_required
def portal_category_edit_view(request, category_id):
    """Edit an existing category."""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            log_activity(request.user, "CATEGORY_UPDATED", f"Updated category {category.name}")
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('portal:categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'portal/category_form.html', {'form': form, 'category': category, 'title': f'Edit Category: {category.name}'})


# --- ORDER MANAGEMENT ---

@staff_member_required
def portal_orders_list_view(request):
    """View and filter all customer orders."""
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(recipient_name__icontains=query) |
            Q(phone_primary__icontains=query) |
            Q(customer__email__icontains=query)
        )

    return render(request, 'portal/orders_list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'query': query,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required
def portal_order_detail_view(request, order_number):
    """
    Staff/Manager/Owner order management view:
    - View items, delivery details, and customer information
    - Update fulfillment status, payment status, tracking number, internal staff notes
    """
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)

    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save()
            log_activity(
                request.user, 
                "ORDER_STATUS_UPDATED", 
                f"Updated order {order.order_number} to {updated_order.get_status_display()}"
            )
            messages.success(request, f"Order {order.order_number} updated successfully.")
            return redirect('portal:order_detail', order_number=order.order_number)
    else:
        form = OrderStatusUpdateForm(instance=order)

    return render(request, 'portal/order_detail.html', {
        'order': order,
        'form': form,
        'is_owner': request.user.is_owner,
    })


# --- INQUIRIES & MESSAGES ---

@staff_member_required
def portal_inquiries_list_view(request):
    """Manage customer contact messages and quotation queries."""
    inquiries = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'portal/inquiries_list.html', {'inquiries': inquiries})


@staff_member_required
@require_POST
def portal_inquiry_toggle_view(request, inquiry_id):
    """Toggle resolved status of customer inquiry."""
    inquiry = get_object_or_404(ContactMessage, id=inquiry_id)
    inquiry.is_resolved = not inquiry.is_resolved
    inquiry.save()
    status_label = "resolved" if inquiry.is_resolved else "pending"
    messages.info(request, f"Inquiry marked as {status_label}.")
    return redirect('portal:inquiries_list')


# --- SITE & CONTENT SETTINGS (OWNER ONLY) ---

@owner_required
def portal_site_settings_view(request):
    """
    STRICTLY OWNER ONLY:
    Allows the business owner to edit company details, contact information,
    WhatsApp number, announcement banner, shipping fees, and policies
    directly through the user-friendly dashboard.
    """
    settings_obj = SiteSettings.get_settings()

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            log_activity(request.user, "SITE_SETTINGS_UPDATED", "Owner updated website branding, contact info, and policies.")
            messages.success(request, "Website and company settings updated successfully!")
            return redirect('portal:site_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, 'portal/site_settings.html', {'form': form})


# --- STAFF ROLES & PERMISSIONS (OWNER ONLY) ---

@owner_required
def portal_staff_list_view(request):
    """
    STRICTLY OWNER ONLY:
    Manage staff roles and user accounts.
    """
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'portal/staff_list.html', {'users': users})


@owner_required
def portal_user_role_edit_view(request, user_id):
    """
    STRICTLY OWNER ONLY:
    Change role of a user (e.g. promote to Order Staff or Manager).
    """
    target_user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent owner from demoting themselves accidentally
    if target_user == request.user:
        messages.warning(request, "You cannot modify your own primary Owner role.")
        return redirect('portal:staff_list')

    if request.method == 'POST':
        form = StaffRoleUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            updated = form.save()
            log_activity(
                request.user, 
                "USER_ROLE_CHANGED", 
                f"Changed role of {updated.email} to {updated.get_role_display()}"
            )
            messages.success(request, f"Updated permissions for {updated.email}.")
            return redirect('portal:staff_list')
    else:
        form = StaffRoleUpdateForm(instance=target_user)

    return render(request, 'portal/staff_role_form.html', {'form': form, 'target_user': target_user})


# --- AUDIT LOGS (OWNER ONLY) ---

@owner_required
def portal_audit_logs_view(request):
    """
    STRICTLY OWNER ONLY:
    View security activity logs, permission changes, and updates.
    """
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    return render(request, 'portal/audit_logs.html', {'logs': logs})
