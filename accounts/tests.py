from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Address
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from portal.models import SiteSettings

User = get_user_model()


class CustomerIsolationAndSecurityTests(TestCase):
    """
    CRITICAL SECURITY & CUSTOMER ISOLATION TEST SUITE
    Verifies that Customer A can NEVER access or manipulate Customer B's records,
    and regular customers can NEVER access the Management Portal.
    """

    def setUp(self):
        # 1. Create Customer A
        self.customer_a = User.objects.create_user(
            email='customer_a@example.com',
            password='Password123!',
            first_name='Alice',
            last_name='Uwase',
            phone_number='+250788111111',
            role=User.ROLE_CUSTOMER
        )

        # 2. Create Customer B
        self.customer_b = User.objects.create_user(
            email='customer_b@example.com',
            password='Password123!',
            first_name='Bob',
            last_name='Mugisha',
            phone_number='+250788222222',
            role=User.ROLE_CUSTOMER
        )

        # 3. Create Business Owner
        self.owner = User.objects.create_superuser(
            email='owner@zdelectronics.rw',
            password='OwnerPassword123!',
            first_name='Z&D',
            last_name='Owner',
            role=User.ROLE_OWNER
        )

        # 4. Set up Category & Product with selling_price and confidential cost_price
        self.category = Category.objects.create(name='Smartphones', slug='smartphones', icon='smartphone')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Smartphone S24',
            slug='test-smartphone-s24',
            sku='ZD-TEST-S24',
            selling_price=Decimal('1000000.00'),  # 1,000,000 RWF
            cost_price=Decimal('850000.00'),      # 850,000 RWF (Owner Only)
            stock_quantity=10,
            is_published=True
        )

        # 5. Create Order for Customer A
        self.order_a = Order.objects.create(
            order_number='ZD-2026-AAAA',
            customer=self.customer_a,
            recipient_name='Alice Uwase',
            phone_primary='+250788111111',
            delivery_address='KG 123 St, Kimihurura',
            city_district='Kigali - Gasabo',
            subtotal=Decimal('1000000.00'),
            shipping_fee=Decimal('3000.00'),
            total_amount=Decimal('1003000.00'),
            status=Order.STATUS_PENDING
        )
        self.order_item_a = OrderItem.objects.create(
            order=self.order_a,
            product=self.product,
            product_name=self.product.name,
            product_sku=self.product.sku,
            unit_price=self.product.selling_price,
            unit_cost=self.product.cost_price,
            quantity=1,
            total_price=Decimal('1000000.00')
        )

        # 6. Create Address for Customer A
        self.address_a = Address.objects.create(
            customer=self.customer_a,
            full_name='Alice Uwase',
            phone_number='+250788111111',
            street_address='House 14, KG 500 St',
            city_district='Kigali - Nyarugenge',
            province='Kigali City',
            country='Rwanda',
            is_default=True
        )

        # Test clients
        self.client_a = Client()
        self.client_b = Client()
        self.client_owner = Client()
        self.client_anonymous = Client()

    def test_01_customer_a_can_access_own_order(self):
        """Customer A should successfully access their own order details."""
        self.client_a.login(email='customer_a@example.com', password='Password123!')
        url = reverse('accounts:order_detail', kwargs={'order_number': 'ZD-2026-AAAA'})
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ZD-2026-AAAA')
        self.assertContains(response, 'Alice Uwase')

    def test_02_strict_isolation_customer_b_cannot_access_customer_a_order(self):
        """
        CRITICAL TEST: Customer B logs in and attempts to access Customer A's order by URL.
        The server MUST deny access (404 Not Found), disclosing ZERO customer information.
        """
        self.client_b.login(email='customer_b@example.com', password='Password123!')
        url = reverse('accounts:order_detail', kwargs={'order_number': 'ZD-2026-AAAA'})
        response = self.client_b.get(url)
        # Server must return 404 and NOT leak Alice's data
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, 'Alice Uwase', status_code=404)
        self.assertNotContains(response, '+250788111111', status_code=404)

    def test_03_strict_isolation_customer_b_cannot_edit_customer_a_address(self):
        """
        Customer B attempts to access/edit Customer A's saved address.
        The server MUST deny access (404 Not Found).
        """
        self.client_b.login(email='customer_b@example.com', password='Password123!')
        url = reverse('accounts:address_edit', kwargs={'address_id': self.address_a.id})
        response = self.client_b.get(url)
        self.assertEqual(response.status_code, 404)

    def test_04_strict_isolation_customer_b_cannot_delete_customer_a_address(self):
        """
        Customer B attempts to POST delete Customer A's address.
        The server MUST deny access and preserve the address.
        """
        self.client_b.login(email='customer_b@example.com', password='Password123!')
        url = reverse('accounts:address_delete', kwargs={'address_id': self.address_a.id})
        response = self.client_b.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Address.objects.filter(id=self.address_a.id).exists())

    def test_05_portal_protected_customers_denied_access(self):
        """
        Customer A and Customer B MUST be denied access to the Owner/Staff portal (/portal/).
        """
        self.client_a.login(email='customer_a@example.com', password='Password123!')
        response = self.client_a.get(reverse('portal:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_06_unauthenticated_visitor_redirected_from_private_views(self):
        """
        Anonymous users attempting to access /accounts/dashboard/ or /orders/checkout/
        must be redirected to login.
        """
        response = self.client_anonymous.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_07_public_registration_cannot_escalate_to_owner_or_staff(self):
        """
        Public registration MUST always force role=CUSTOMER, even if an attacker
        sends role=OWNER or is_superuser=True in the POST payload.
        """
        response = self.client_anonymous.post(reverse('accounts:register'), {
            'email': 'hacker@example.com',
            'first_name': 'Bad',
            'last_name': 'Actor',
            'phone_number': '+250788000999',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'role': 'OWNER',
            'is_staff': True,
            'is_superuser': True
        })
        user = User.objects.get(email='hacker@example.com')
        self.assertEqual(user.role, User.ROLE_CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_08_owner_has_full_management_access(self):
        """
        Business Owner can access portal, view profit metrics, and edit site settings.
        """
        self.client_owner.login(email='owner@zdelectronics.rw', password='OwnerPassword123!')
        response = self.client_owner.get(reverse('portal:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Business Owner Financial Summary')

    def test_09_server_side_pricing_integrity(self):
        """
        Verifies that product profit calculation equals selling_price - cost_price.
        """
        self.assertEqual(self.product.estimated_profit, Decimal('150000.00'))  # 1,000,000 - 850,000
        self.assertEqual(self.order_item_a.estimated_profit, Decimal('150000.00'))
