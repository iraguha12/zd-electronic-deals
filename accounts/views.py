from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import CustomUser, Address
from .forms import CustomerRegistrationForm, CustomerLoginForm, CustomerProfileForm, AddressForm
from .permissions import customer_required, get_isolated_customer_order, get_isolated_customer_address
from orders.models import Order


def register_view(request):
    """
    Public customer registration.
    Enforces strict role assignment (always CUSTOMER), secure password hashing,
    and immediate login upon successful registration.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Z&D ELECTRONIC DEALS, {user.first_name}! Your account is active.")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Secure login view for customers and authorized staff.
    """
    if request.user.is_authenticated:
        if request.user.is_staff_member:
            return redirect('portal:dashboard')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            
            from django.contrib.auth import authenticate
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                    
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    if user.is_staff_member:
                        return redirect('portal:dashboard')
                    return redirect('accounts:dashboard')
                else:
                    messages.error(request, "This account has been deactivated. Please contact Z&D support.")
            else:
                messages.error(request, "Invalid email address or password. Please try again.")
    else:
        form = CustomerLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Secure logout that terminates session and flushes cookies."""
    logout(request)
    messages.info(request, "You have been signed out safely. Thank you for visiting Z&D.")
    return redirect('pages:home')


@customer_required
def dashboard_view(request):
    """
    Customer dashboard with strict isolation.
    Shows only the logged-in customer's orders and addresses.
    """
    user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]
    total_orders_count = Order.objects.filter(customer=request.user).count()
    addresses = Address.objects.filter(customer=request.user).order_by('-is_default')
    
    context = {
        'recent_orders': user_orders,
        'total_orders_count': total_orders_count,
        'addresses': addresses,
        'user': request.user,
    }
    return render(request, 'accounts/dashboard.html', context)


@customer_required
def orders_list_view(request):
    """
    STRICT CUSTOMER ISOLATION:
    Returns ONLY orders belonging to request.user.
    """
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'accounts/orders_list.html', {'orders': orders})


@customer_required
def order_detail_view(request, order_number):
    """
    STRICT CUSTOMER ISOLATION:
    Customer can ONLY view their own order details.
    Access to another customer's order number will 404 without leaking data.
    """
    order = get_isolated_customer_order(request, order_number)
    return render(request, 'accounts/order_detail.html', {'order': order})


@customer_required
def addresses_view(request):
    """List of customer's saved delivery addresses."""
    addresses = Address.objects.filter(customer=request.user).order_by('-is_default', '-created_at')
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


@customer_required
def address_add_view(request):
    """Add a new delivery address linked to request.user."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = request.user
            # If first address, make default
            if not Address.objects.filter(customer=request.user).exists():
                address.is_default = True
            address.save()
            messages.success(request, "Delivery address saved successfully.")
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add New Delivery Address'})


@customer_required
def address_edit_view(request, address_id):
    """STRICT ISOLATION: Customer can only edit their own address."""
    address = get_isolated_customer_address(request, address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery address updated.")
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Delivery Address'})


@customer_required
@require_POST
def address_delete_view(request, address_id):
    """STRICT ISOLATION: Customer can only delete their own address."""
    address = get_isolated_customer_address(request, address_id)
    address.delete()
    messages.success(request, "Address removed.")
    return redirect('accounts:addresses')


@customer_required
def profile_edit_view(request):
    """Edit permitted personal profile information."""
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('accounts:dashboard')
    else:
        form = CustomerProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@customer_required
def password_change_view(request):
    """Change customer password with secure session update."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password was changed successfully.")
            return redirect('accounts:dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})


@customer_required
def request_account_deletion_view(request):
    """Privacy-compliant account deletion request."""
    if request.method == 'POST':
        # Mark inactive and record privacy request
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.info(request, "Your account deletion request has been processed. Your session has ended.")
        return redirect('pages:home')
    return render(request, 'accounts/account_deletion_confirm.html')
