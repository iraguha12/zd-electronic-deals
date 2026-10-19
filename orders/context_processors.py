def cart_processor(request):
    """
    Computes total cart quantity for the header badge
    directly from the session.
    """
    cart = request.session.get('cart', {})
    total_qty = 0
    if isinstance(cart, dict):
        for pid, qty in cart.items():
            if isinstance(qty, int):
                total_qty += qty
            elif isinstance(qty, dict) and 'quantity' in qty:
                total_qty += qty['quantity']
    return {
        'cart_count': total_qty
    }
