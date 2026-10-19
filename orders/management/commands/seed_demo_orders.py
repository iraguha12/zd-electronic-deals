from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Address
from catalog.models import Product
from orders.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Creates two independent customer accounts and sample orders in Rwandan Francs (RWF)'

    def handle(self, *args, **options):
        # 1. Customer 1
        c1, _ = CustomUser.objects.get_or_create(
            email='jean.claud@rwanda.rw',
            defaults={
                'first_name': 'Jean-Claude',
                'last_name': 'Nshimiyimana',
                'phone_number': '+250 788 111 222',
                'role': CustomUser.ROLE_CUSTOMER,
                'is_active': True,
                'is_email_verified': True
            }
        )
        c1.set_password('CustomerPass123!')
        c1.save()

        Address.objects.get_or_create(
            customer=c1,
            full_name='Jean-Claude Nshimiyimana',
            defaults={
                'phone_number': '+250 788 111 222',
                'street_address': 'Building 4, KG 17 Ave',
                'city_district': 'Kigali - Gasabo (Kacyiru)',
                'province': 'Kigali City',
                'country': 'Rwanda',
                'is_default': True
            }
        )

        # 2. Customer 2
        c2, _ = CustomUser.objects.get_or_create(
            email='marie.grace@rwanda.rw',
            defaults={
                'first_name': 'Marie-Grace',
                'last_name': 'Uwamahoro',
                'phone_number': '+250 788 333 444',
                'role': CustomUser.ROLE_CUSTOMER,
                'is_active': True,
                'is_email_verified': True
            }
        )
        c2.set_password('CustomerPass123!')
        c2.save()

        Address.objects.get_or_create(
            customer=c2,
            full_name='Marie-Grace Uwamahoro',
            defaults={
                'phone_number': '+250 788 333 444',
                'street_address': 'Plot 12, Gisenyi Main Road',
                'city_district': 'Rubavu District',
                'province': 'Western Province',
                'country': 'Rwanda',
                'is_default': True
            }
        )

        # 3. Create sample order for Customer 1
        iphone = Product.objects.filter(sku='ZD-IP15PM-256').first()
        anker = Product.objects.filter(sku='ZD-ANK-65W').first()

        if iphone and anker:
            o1, created = Order.objects.get_or_create(
                order_number='ZD-2026-1001',
                defaults={
                    'customer': c1,
                    'recipient_name': 'Jean-Claude Nshimiyimana',
                    'phone_primary': '+250 788 111 222',
                    'delivery_address': 'Building 4, KG 17 Ave, Kacyiru',
                    'city_district': 'Kigali - Gasabo',
                    'province': 'Kigali City',
                    'country': 'Rwanda',
                    'subtotal': iphone.selling_price + anker.selling_price,
                    'shipping_fee': Decimal('3000.00'),
                    'total_amount': iphone.selling_price + anker.selling_price + Decimal('3000.00'),
                    'status': Order.STATUS_SOURCING,
                    'payment_status': 'CONFIRMED_ON_DELIVERY',
                    'payment_method': 'WHATSAPP_CONFIRMED',
                    'tracking_number': 'RW-AIR-8921-SZ',
                    'staff_notes': 'Sourced from Shenzhen authorized distributor. Flight ET-304 booked.'
                }
            )
            if created:
                OrderItem.objects.create(
                    order=o1,
                    product=iphone,
                    product_name=iphone.name,
                    product_sku=iphone.sku,
                    unit_price=iphone.selling_price,
                    unit_cost=iphone.cost_price,
                    quantity=1,
                    total_price=iphone.selling_price
                )
                OrderItem.objects.create(
                    order=o1,
                    product=anker,
                    product_name=anker.name,
                    product_sku=anker.sku,
                    unit_price=anker.selling_price,
                    unit_cost=anker.cost_price,
                    quantity=1,
                    total_price=anker.selling_price
                )

        # 4. Create sample order for Customer 2
        macbook = Product.objects.filter(sku='ZD-MBA-M2-MID').first()
        if macbook:
            o2, created2 = Order.objects.get_or_create(
                order_number='ZD-2026-1002',
                defaults={
                    'customer': c2,
                    'recipient_name': 'Marie-Grace Uwamahoro',
                    'phone_primary': '+250 788 333 444',
                    'delivery_address': 'Plot 12, Gisenyi Main Road',
                    'city_district': 'Rubavu District',
                    'province': 'Western Province',
                    'country': 'Rwanda',
                    'subtotal': macbook.selling_price,
                    'shipping_fee': Decimal('6000.00'),
                    'total_amount': macbook.selling_price + Decimal('6000.00'),
                    'status': Order.STATUS_PENDING,
                    'payment_status': 'UNPAID',
                    'payment_method': 'MOMO_AIRTEL',
                    'staff_notes': 'Awaiting customer WhatsApp confirmation on delivery date in Rubavu.'
                }
            )
            if created2:
                OrderItem.objects.create(
                    order=o2,
                    product=macbook,
                    product_name=macbook.name,
                    product_sku=macbook.sku,
                    unit_price=macbook.selling_price,
                    unit_cost=macbook.cost_price,
                    quantity=1,
                    total_price=macbook.selling_price
                )

        self.stdout.write(self.style.SUCCESS("Sample customer accounts and isolated orders seeded successfully!"))
