from .models import SiteSettings


def site_settings_processor(request):
    """
    Supplies the dynamic company branding, WhatsApp number, announcement banner,
    and phone numbers editable by the owner to all pages.
    """
    settings = SiteSettings.get_settings()
    return {
        'site_settings': settings,
        'CURRENCY_CODE': 'RWF',
        'CURRENCY_SYMBOL': 'RWF',
    }
