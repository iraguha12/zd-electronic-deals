import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from catalog.models import Product


class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_SOURCING = 'SOURCING_CHINA'
    STATUS_TRANSIT = 'IN_TRANSIT'
    STATUS_KIGALI_HUB = 'READY_KIGALI'
    STATUS_OUT_DELIVERY = 'OUT_FOR_DELIVERY'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_CONFIRMED, 'Confirmed & Scheduled'),
        (STATUS_SOURCING, 'Sourcing from China Factory'),
        (STATUS_TRANSIT, 'In Transit to Rwanda'),
        (STATUS_KIGALI_HUB, 'Arrived at Kigali Hub'),
        (STATUS_OUT_DELIVERY, 'Out for Delivery'),
        (STATUS_DELIVERED, 'Delivered & Complete'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    ORDER_TYPE_CHOICES = [
        ('DIRECT_PURCHASE', 'Standard Purchase'),
        ('CUSTOM_QUOTE', 'China Custom Sourcing Request'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid (Quote / Pending)'),
        ('CONFIRMED_ON_DELIVERY', 'Payment on Delivery / Pickup'),
        ('PAID', 'Paid in Full'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('WHATSAPP_CONFIRMED', 'WhatsApp Direct Order / Confirmation'),
        ('MOMO_AIRTEL', 'Mobile Money (MTN MoMo / Airtel Money)'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery (Kigali Only)'),
        ('BANK_TRANSFER', 'Bank Transfer / Wire'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=40, unique=True, editable=False)
    
    # Ownership: Customer ForeignKey with cascade delete prevention if needed
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    order_type = models.CharField(max_length=30, choices=ORDER_TYPE_CHOICES, default='DIRECT_PURCHASE')
    
    # Recipient & Delivery Snapshot
    recipient_name = models.CharField(max_length=150)
    phone_primary = models.CharField(max_length=30)
    phone_backup = models.CharField(max_length=30, blank=True)
    delivery_address = models.TextField()
    city_district = models.CharField(max_length=100)
    province = models.CharField(max_length=100, default="Kigali City")
    country = models.CharField(max_length=100, default="Rwanda")
    delivery_notes = models.TextField(blank=True)

    # Financial breakdown (in RWF)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Payment details
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='WHATSAPP_CONFIRMED')
    tracking_number = models.CharField(max_length=120, blank=True, help_text="Courier or cargo flight tracking code")
    
    # Confidential internal operations (NEVER shown to customer)
    staff_notes = models.TextField(blank=True, help_text="Internal notes visible only to Staff, Managers, and Owner")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Order'
        verbose_name_plural = 'Customer Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.recipient_name} ({self.get_status_display()})"

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_order_profit(self):
        """Owner-only financial calculation: total price minus procurement cost"""
        return sum(item.estimated_profit for item in self.items.all())

    def recalculate_totals(self):
        """Server-side calculation of order totals; never trusts client figures"""
        calculated_subtotal = sum(item.total_price for item in self.items.all())
        self.subtotal = calculated_subtotal
        self.total_amount = calculated_subtotal + self.shipping_fee
        self.save(update_fields=['subtotal', 'total_amount'])


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    
    # Snapshots to preserve order integrity if original product is updated or deleted later
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True)
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2) # Selling price in RWF
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00')) # Confidential Owner cost
    
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"

    @property
    def total_cost(self):
        return self.unit_cost * self.quantity

    @property
    def estimated_profit(self):
        """Calculates profit for this item line (Owner Only)"""
        return self.total_price - self.total_cost

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
