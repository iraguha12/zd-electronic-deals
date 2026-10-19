from django.shortcuts import render, redirect
from django.contrib import messages
from catalog.models import Product, Category
from portal.models import SiteSettings
from .models import ContactMessage
import urllib.parse


def home_view(request):
    """
    Homepage featuring:
    - Hero section with brand colors (Navy #0B1B3D, Royal Blue #1E56A0, Gold #D4AF37)
    - "BEFORE YOU BUY ELECTRONICS, ASK Z&D"
    - Category quick filters
    - Featured Products & New Arrivals
    - Direct China Sourcing Trust Section
    """
    settings = SiteSettings.get_settings()
    featured_products = Product.objects.filter(is_featured=True, is_published=True).select_related('category').prefetch_related('images')[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, is_published=True).select_related('category').prefetch_related('images')[:8]
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')[:8]

    # Pre-formatted generic WhatsApp inquiry
    wa_text = "Hello Z&D Electronic Deals! I visited your website and would like to ask about an electronic device before I buy."
    hero_whatsapp_url = f"https://wa.me/{settings.whatsapp_number}?text={urllib.parse.quote(wa_text)}"

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'site_settings': settings,
        'hero_whatsapp_url': hero_whatsapp_url,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    """Company background, mission, and direct China sourcing infrastructure."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/about.html', {'site_settings': settings})


def contact_view(request):
    """Contact page with interactive inquiry form and direct WhatsApp links."""
    settings = SiteSettings.get_settings()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, "Thank you! Your message has been sent to our customer support team.")
            return redirect('pages:contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    # WhatsApp contact link
    wa_text = "Hello Z&D Team! I have a customer enquiry regarding your electronics sourcing and delivery."
    wa_url = f"https://wa.me/{settings.whatsapp_number}?text={urllib.parse.quote(wa_text)}"

    return render(request, 'pages/contact.html', {
        'site_settings': settings,
        'contact_whatsapp_url': wa_url
    })


def faqs_view(request):
    """Frequently asked questions for electronics buyers."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/faqs.html', {'site_settings': settings})


def shipping_view(request):
    """Shipping, customs, and China-to-Rwanda delivery information."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/shipping.html', {'site_settings': settings})


def returns_view(request):
    """Return, refund, and warranty policy."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/returns.html', {'site_settings': settings})


def privacy_view(request):
    """Privacy policy detailing account isolation and data protection."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/privacy.html', {'site_settings': settings})


def terms_view(request):
    """Terms and conditions."""
    settings = SiteSettings.get_settings()
    return render(request, 'pages/terms.html', {'site_settings': settings})
