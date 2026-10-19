import random
import string
import urllib.parse
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Order, OrderItem
from catalog.models import Product
from accounts.models import Address
from portal.models import SiteSettings


def get_cart_items(request):
    """
    Helper function to unpack cart stored in session and calculate totals.
    Always uses live database selling_price to prevent client price tampering.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0.00')

    for product_id_str, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id_str, is_published=True)
            qty = item_data if isinstance(item_data, int) else item_data.get('quantity', 1)
            line_total = product.selling_price * qty
            subtotal += line_total
            cart_items.append({
                'product': product,
                'quantity': qty,
                'line_total': line_total,
            })
        except Product.DoesNotExist:
            continue

    return cart_items, subtotal


def cart_view(request):
    """View shopping cart contents and shipping estimate."""
    cart_items, subtotal = get_cart_items(request)
    settings = SiteSettings.get_settings()
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'standard_shipping': settings.standard_kigali_shipping_rwf,
        'upcountry_shipping': settings.upcountry_shipping_rwf,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def cart_add_view(request, product_id):
    """Add a product to cart with server-side quantity validation."""
    product = get_object_or_404(Product, id=product_id, is_published=True)
    try:
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            qty = 1
    except (ValueError, TypeError):
        qty = 1

    cart = request.session.get('cart', {})
    product_key = str(product.id)

    if product_key in cart:
        current_qty = cart[product_key] if isinstance(cart[product_key], int) else cart[product_key].get('quantity', 1)
        cart[product_key] = current_qty + qty
    else:
        cart[product_key] = qty

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"Added {qty}x {product.name} to your cart.")
    
    redirect_target = request.POST.get('next', 'orders:cart')
    if redirect_target == 'checkout':
        return redirect('orders:checkout')
    return redirect(redirect_target)


@require_POST
def cart_update_view(request, product_id):
    """Update item quantity or delete from cart."""
    product_key = str(product_id)
    action = request.POST.get('action')
    cart = request.session.get('cart', {})

    if product_key in cart:
        if action == 'remove':
            del cart[product_key]
            messages.info(request, "Item removed from cart.")
        elif action == 'update':
            try:
                new_qty = int(request.POST.get('quantity', 1))
                if new_qty > 0:
                    cart[product_key] = new_qty
                    messages.success(request, "Cart quantity updated.")
                else:
                    del cart[product_key]
                    messages.info(request, "Item removed from cart.")
            except (ValueError, TypeError):
                pass
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('orders:cart')


def cart_clear_view(request):
    """Clear all items from session cart."""
    request.session['cart'] = {}
    request.session.modified = True
    messages.info(request, "Your cart has been emptied.")
    return redirect('orders:cart')


def checkout_view(request):
    """
    Secure checkout:
    - Calculates server-side prices and totals.
    - Requires customer login (or prompts login/registration with cart preserved).
    - Creates Order and OrderItem records.
    - Prevents price manipulation.
    """
    cart_items, subtotal = get_cart_items(request)
    if not cart_items:
        messages.warning(request, "Your cart is empty. Please select products to continue.")
        return redirect('catalog:product_list')

    if not request.user.is_authenticated:
        messages.info(request, "Please log in or create an account to finalize your order.")
        return redirect(f"{'/accounts/login/'}?next={'/orders/checkout/'}")

    settings = SiteSettings.get_settings()
    default_address = Address.objects.filter(customer=request.user, is_default=True).first()
    if not default_address:
        default_address = Address.objects.filter(customer=request.user).first()

    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name', '').strip()
        phone_primary = request.POST.get('phone_primary', '').strip()
        phone_backup = request.POST.get('phone_backup', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        city_district = request.POST.get('city_district', '').strip()
        province = request.POST.get('province', 'Kigali City').strip()
        country = request.POST.get('country', 'Rwanda').strip()
        delivery_notes = request.POST.get('delivery_notes', '').strip()
        shipping_type = request.POST.get('shipping_type', 'kigali')
        payment_method = request.POST.get('payment_method', 'WHATSAPP_CONFIRMED')

        if not recipient_name or not phone_primary or not delivery_address:
            messages.error(request, "Please fill in all required delivery information.")
            return redirect('orders:checkout')

        # Determine shipping fee based on server-side site settings
        if shipping_type == 'upcountry':
            shipping_fee = settings.upcountry_shipping_rwf
        else:
            shipping_fee = settings.standard_kigali_shipping_rwf

        # Generate unique order number
        year = timezone.now().year
        random_suffix = ''.join(random.choices(string.digits, k=4))
        order_number = f"ZD-{year}-{random_suffix}"
        while Order.objects.filter(order_number=order_number).exists():
            random_suffix = ''.join(random.choices(string.digits, k=4))
            order_number = f"ZD-{year}-{random_suffix}"

        # Create Order record
        order = Order.objects.create(
            order_number=order_number,
            customer=request.user,
            recipient_name=recipient_name,
            phone_primary=phone_primary,
            phone_backup=phone_backup,
            delivery_address=delivery_address,
            city_district=city_district or 'Kigali',
            province=province,
            country=country,
            delivery_notes=delivery_notes,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=subtotal + shipping_fee,
            payment_method=payment_method,
            payment_status='UNPAID',
            status=Order.STATUS_PENDING
        )

        # Create OrderItem records with price and cost snapshots
        for item in cart_items:
            product = item['product']
            qty = item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                unit_price=product.selling_price,
                unit_cost=product.cost_price,
                quantity=qty,
                total_price=product.selling_price * qty
            )

        # Clear session cart
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f"Order {order.order_number} submitted successfully!")
        return redirect('orders:order_confirmation', order_number=order.order_number)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'default_address': default_address,
        'site_settings': settings,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation_view(request, order_number):
    """
    Order confirmation view with strict authorization:
    Customer can only view their own confirmation unless staff.
    Builds a complete, formatted WhatsApp message for one-click verification.
    """
    settings = SiteSettings.get_settings()
    
    if request.user.is_authenticated:
        if request.user.is_staff_member:
            order = get_object_or_404(Order, order_number=order_number)
        else:
            order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    else:
        # If unauthenticated, access is denied
        messages.error(request, "Please log in to review your order details.")
        return redirect('accounts:login')

    items_summary = []
    for item in order.items.all():
        items_summary.append(f"• {item.quantity}x {item.product_name} ({int(item.total_price):,} RWF)")
    items_text = "\n".join(items_summary)

    whatsapp_message = (
        f"🇷🇼 *NEW ORDER CONFIRMATION — Z&D ELECTRONIC DEALS*\n\n"
        f"📋 *Order Number*: {order.order_number}\n"
        f"👤 *Customer*: {order.recipient_name} ({order.phone_primary})\n"
        f"📍 *Delivery Destination*: {order.delivery_address}, {order.city_district}, {order.country}\n\n"
        f"📦 *Ordered Products*:\n{items_text}\n\n"
        f"💵 *Subtotal*: {int(order.subtotal):,} RWF\n"
        f"🚚 *Delivery Fee*: {int(order.shipping_fee):,} RWF\n"
        f"💰 *TOTAL*: {int(order.total_amount):,} RWF\n"
        f"💳 *Payment Choice*: {order.get_payment_method_display()}\n\n"
        f"Please verify order and confirm delivery schedule. Thank you!"
    )
    encoded_whatsapp_url = (
        f"https://wa.me/{settings.whatsapp_number}?text={urllib.parse.quote(whatsapp_message)}"
    )

    context = {
        'order': order,
        'whatsapp_url': encoded_whatsapp_url,
        'site_settings': settings,
    }
    return render(request, 'orders/order_confirmation.html', context)
