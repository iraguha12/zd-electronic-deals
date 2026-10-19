import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings


class SiteSettings(models.Model):
    """
    Singleton model allowing the Business Owner to customize the website's
    public details, branding, contact info, shipping rates, and legal policies
    directly from the Owner Dashboard without modifying any code.
    """
    company_name = models.CharField(max_length=150, default="Z&D ELECTRONIC DEALS")
    slogan = models.CharField(max_length=200, default="BEFORE YOU BUY ELECTRONICS, ASK Z&D.")
    
    primary_phone = models.CharField(max_length=40, default="+250 788 123 456")
    whatsapp_number = models.CharField(
        max_length=30, 
        default="250788123456", 
        help_text="Country code + phone without '+' or spaces (e.g. 250788123456 for Rwanda)"
    )
    email_contact = models.EmailField(default="sales@zdelectronics.rw")
    physical_address = models.CharField(
        max_length=255, 
        default="Kigali Commercial District, Rwanda | Sourcing Offices: Shenzhen & Guangzhou, China"
    )
    
    # Top announcement banner
    announcement_banner = models.CharField(
        max_length=255, 
        default="🇷🇼 Direct China Electronics Sourcing to Rwanda & Worldwide | Verified Quality & Fair Prices"
    )
    show_announcement = models.BooleanField(default=True)

    # Shipping fees in Rwandan Francs (RWF)
    standard_kigali_shipping_rwf = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('3000.00'),
        help_text="Standard Kigali express delivery fee in RWF"
    )
    upcountry_shipping_rwf = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('6000.00'),
        help_text="Upcountry Rwanda delivery fee in RWF (Rubavu, Musanze, Huye, etc.)"
    )

    # Editable website content
    about_company = models.TextField(
        default="Z&D ELECTRONIC DEALS is a premier electronics trading and direct sourcing firm connecting Rwandan consumers, professionals, and enterprises directly with vetted electronic manufacturers in Shenzhen and Guangzhou, China. We eliminate inflated intermediary markups while providing strict multi-point hardware inspection, warranty coverage, and reliable delivery directly to your door in Rwanda and worldwide."
    )
    shipping_guide = models.TextField(
        default="### Direct China-to-Rwanda Logistics\n- **In-Stock Rwanda Warehouse**: Delivery within 2 to 24 hours in Kigali, 24-48 hours upcountry.\n- **Direct China Factory Orders**: Express Air Cargo arrives within 7 to 12 business days. Sea cargo for bulk commercial consignments arrives in 35 to 45 days.\n- **Quality Assurance**: Every device sourced from China undergoes physical testing, serial validation, and charging verification at our Shenzhen dispatch hub before departure to Kigali."
    )
    return_policy = models.TextField(
        default="Z&D ELECTRONIC DEALS guarantees the authenticity and working condition of all devices. We provide replacement or refund for verified hardware defects reported within 7 days of delivery, supported by official warranty terms."
    )
    privacy_policy = models.TextField(
        default="We respect your strict privacy. Your personal information, contact numbers, and delivery addresses are collected solely to fulfill orders and provide direct customer support. We never sell, rent, or expose customer records to any third party."
    )
    terms_conditions = models.TextField(
        default="By ordering from Z&D ELECTRONIC DEALS, you agree to our transparent sourcing and delivery terms. Pre-orders sourced on request require confirmation prior to dispatch."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Website & Company Settings'
        verbose_name_plural = 'Website & Company Settings'

    def __str__(self):
        return f"{self.company_name} Configuration"

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class AuditLog(models.Model):
    """
    Immutable activity and security log for critical actions:
    e.g. price updates, stock adjustments, order status changes, staff permissions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    ip_address = models.CharField(max_length=60, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.email if self.user else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {user_str}: {self.action}"
