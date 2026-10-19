from .models import Category


def categories_processor(request):
    """Makes active product categories available across all templates."""
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')
    return {
        'nav_categories': categories
    }
