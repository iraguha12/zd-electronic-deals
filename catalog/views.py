from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product
from portal.models import SiteSettings
import urllib.parse


def product_list_view(request):
    """
    Public product catalogue with search and category filtering.
    Confidential cost_price is NEVER sent to frontend templates.
    """
    products = Product.objects.filter(is_published=True).select_related('category').prefetch_related('images')
    
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    origin_filter = request.GET.get('origin', '').strip()
    sort = request.GET.get('sort', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if origin_filter == 'rwanda':
        products = products.filter(in_stock_in_rwanda=True)
    elif origin_filter == 'china':
        products = products.filter(is_sourced_from_china=True)

    if sort == 'price_low':
        products = products.order_by('selling_price')
    elif sort == 'price_high':
        products = products.order_by('-selling_price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-created_at')

    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_query': query,
        'origin_filter': origin_filter,
        'sort_by': sort,
        'total_count': products.count(),
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail_view(request, slug):
    """
    Detailed product showcase:
    - High-resolution gallery
    - Detailed specifications
    - Stock & sourcing indicators (China import / Kigali stock)
    - Direct WhatsApp Inquiry / Quote link generator
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug,
        is_published=True
    )
    
    # Related products in same category
    related_products = Product.objects.filter(
        category=product.category,
        is_published=True
    ).exclude(pk=product.pk)[:4]

    # Generate pre-formatted WhatsApp inquiry message
    settings = SiteSettings.get_settings()
    whatsapp_text = (
        f"Hello Z&D Electronic Deals!\n\n"
        f"I am interested in:\n"
        f"📦 *Product*: {product.name}\n"
        f"🔖 *Model/SKU*: {product.sku}\n"
        f"💰 *Listed Price*: {int(product.selling_price):,} RWF\n"
        f"Please provide quotation/availability details. Thank you!"
    )
    encoded_whatsapp_url = (
        f"https://wa.me/{settings.whatsapp_number}?text={urllib.parse.quote(whatsapp_text)}"
    )

    context = {
        'product': product,
        'related_products': related_products,
        'whatsapp_url': encoded_whatsapp_url,
    }
    return render(request, 'catalog/product_detail.html', context)
