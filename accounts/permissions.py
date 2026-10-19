import uuid
from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from django.http import Http404


def customer_required(view_func):
    """
    Ensures the user is authenticated.
    Redirects unauthenticated visitors to login with next-url preserved.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to your account to continue.")
            return redirect(f"{'/accounts/login/'}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_member_required(view_func):
    """
    Ensures the user is an authorized Staff Member, Manager, or Owner.
    Regular customers are strictly denied with 403 Forbidden.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{'/accounts/login/'}?next={request.path}")
        if not request.user.is_staff_member:
            raise PermissionDenied("Access restricted to authorized Z&D operations staff.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def manager_required(view_func):
    """
    Ensures the user is a Manager or Business Owner.
    Order staff and customers are denied.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{'/accounts/login/'}?next={request.path}")
        if not request.user.is_manager_or_above:
            raise PermissionDenied("Operations Manager or Business Owner authorization required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def owner_required(view_func):
    """
    Ensures the user is the Business Owner.
    Protects profit calculations, cost prices, staff role delegation,
    and business configuration.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{'/accounts/login/'}?next={request.path}")
        if not request.user.is_owner:
            raise PermissionDenied("Access strictly restricted to the Business Owner.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_isolated_customer_order(request, order_number_or_id):
    """
    STRICT CUSTOMER ISOLATION HELPER:
    - If customer: queries ONLY orders where customer=request.user.
      Attempting to view another customer's order will ALWAYS raise Http404 (revealing no information).
    - If staff/manager/owner: permitted to view any order for fulfillment.
    - Handles order numbers and UUID ids cleanly without leaking or crashing.
    """
    from orders.models import Order
    qs = Order.objects.prefetch_related('items')
    if not request.user.is_staff_member:
        qs = qs.filter(customer=request.user)

    # 1. Match by order_number (e.g. ZD-2026-AAAA)
    order = qs.filter(order_number=order_number_or_id).first()
    if order:
        return order

    # 2. Match by UUID id if a valid UUID string is passed
    try:
        parsed_uuid = uuid.UUID(str(order_number_or_id))
        order = qs.filter(id=parsed_uuid).first()
        if order:
            return order
    except (ValueError, TypeError, ValidationError):
        pass

    # Never reveal whether another customer owns this order
    raise Http404("Order not found or access denied.")


def get_isolated_customer_address(request, address_id):
    """
    STRICT ADDRESS ISOLATION HELPER:
    Enforces that addresses can only be viewed or modified by the customer who owns them.
    """
    from accounts.models import Address
    try:
        parsed_uuid = uuid.UUID(str(address_id))
        return get_object_or_404(Address, id=parsed_uuid, customer=request.user)
    except (ValueError, TypeError, ValidationError):
        raise Http404("Address not found or access denied.")
