import uuid
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, default='cpu', help_text="Lucide icon name (e.g. smartphone, laptop, zap, headphones, watch)")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    sku = models.CharField(max_length=80, unique=True, help_text="Stock Keeping Unit / Model Code")
    short_description = models.CharField(max_length=320, help_text="Brief summary for product cards and search results")
    description = models.TextField(help_text="Full detailed product description")
    specifications = models.JSONField(default=dict, blank=True, help_text="Key-value pairs of technical specifications")
    
    # Financial fields (Currency: Rwandan Francs RWF)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Customer selling price in Rwandan Francs (RWF)")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="CONFIDENTIAL: Purchase & shipping cost from China in RWF (Owner only)")
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    
    # Sourcing & Origin
    is_sourced_from_china = models.BooleanField(default=True, help_text="Sourced directly from China manufacturers")
    in_stock_in_rwanda = models.BooleanField(default=False, help_text="Currently on hand in Rwanda warehouse/showroom")
    requires_quote = models.BooleanField(default=False, help_text="Price requires confirmation / custom order from China")
    
    # Visibility
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    warranty_info = models.CharField(max_length=200, default="Official Z&D Warranty & Quality Inspection")
    estimated_delivery_days = models.CharField(
        max_length=150, 
        default="Same-day delivery in Kigali | 7-14 days for direct China factory orders"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{str(self.sku).lower()}"
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def estimated_profit(self):
        """Available exclusively to Business Owner"""
        return self.selling_price - self.cost_price

    @property
    def profit_margin_percent(self):
        """Margin calculation for business analytics"""
        if self.selling_price > 0:
            return round(((self.selling_price - self.cost_price) / self.selling_price) * 100, 1)
        return 0

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Web URL for cloud-hosted product image")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'display_order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def get_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/placeholder-product.svg"
