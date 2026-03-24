"""
Functional tests for the Sales and Inventory Management System.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from products.models import Product, Category
from inventory.models import Inventory, InventoryMovement
from sales.models import Sale, SaleDetail


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin', password='Admin1234!', email='admin@test.com',
            role=User.ADMIN
        )
        self.seller = User.objects.create_user(
            username='seller', password='Seller1234!', email='seller@test.com',
            role=User.SALESPERSON
        )

    def test_login_page_accessible(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_redirects_when_not_logged_in(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertRedirects(resp, '/accounts/login/?next=/', fetch_redirect_response=False)

    def test_admin_login(self):
        resp = self.client.post(reverse('login'), {'username': 'admin', 'password': 'Admin1234!'})
        self.assertRedirects(resp, reverse('dashboard'))

    def test_seller_login(self):
        resp = self.client.post(reverse('login'), {'username': 'seller', 'password': 'Seller1234!'})
        self.assertRedirects(resp, reverse('dashboard'))

    def test_user_role_methods(self):
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.is_salesperson())
        self.assertTrue(self.seller.is_salesperson())
        self.assertFalse(self.seller.is_admin())


class ProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin2', password='Admin1234!', email='admin2@test.com',
            role=User.ADMIN
        )
        self.client.login(username='admin2', password='Admin1234!')
        self.category = Category.objects.create(name='Electrónica', description='Electrónicos')

    def test_product_list(self):
        resp = self.client.get(reverse('product_list'))
        self.assertEqual(resp.status_code, 200)

    def test_create_product_creates_inventory(self):
        resp = self.client.post(reverse('product_create'), {
            'code': 'TEST001',
            'name': 'Producto de Prueba',
            'description': 'Descripción',
            'category': self.category.pk,
            'purchase_price': '100.00',
            'sale_price': '150.00',
            'is_active': True,
        })
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Inventory.objects.count(), 1)

    def test_category_create(self):
        resp = self.client.post(reverse('category_create'), {
            'name': 'Ropa',
            'description': 'Ropa y accesorios',
        })
        self.assertEqual(Category.objects.count(), 2)


class InventoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin3', password='Admin1234!', email='admin3@test.com',
            role=User.ADMIN
        )
        self.client.login(username='admin3', password='Admin1234!')
        self.product = Product.objects.create(
            code='P001', name='Test', purchase_price='10', sale_price='20'
        )
        self.inventory = Inventory.objects.create(product=self.product, quantity=10, minimum_stock=3)

    def test_inventory_list(self):
        resp = self.client.get(reverse('inventory_list'))
        self.assertEqual(resp.status_code, 200)

    def test_stock_in_movement(self):
        resp = self.client.post(reverse('inventory_adjust', args=[self.inventory.pk]), {
            'movement_type': InventoryMovement.IN,
            'quantity': 5,
            'reason': 'Reposición',
        })
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 15)

    def test_stock_out_movement(self):
        resp = self.client.post(reverse('inventory_adjust', args=[self.inventory.pk]), {
            'movement_type': InventoryMovement.OUT,
            'quantity': 4,
            'reason': 'Despacho',
        })
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 6)

    def test_stock_out_fails_when_insufficient(self):
        resp = self.client.post(reverse('inventory_adjust', args=[self.inventory.pk]), {
            'movement_type': InventoryMovement.OUT,
            'quantity': 100,
            'reason': 'Salida excesiva',
        })
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)  # unchanged

    def test_low_stock_detection(self):
        self.inventory.quantity = 2
        self.inventory.save()
        self.assertTrue(self.inventory.is_low_stock)

    def test_is_not_low_stock(self):
        self.assertFalse(self.inventory.is_low_stock)


class SaleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin4', password='Admin1234!', email='admin4@test.com',
            role=User.ADMIN
        )
        self.client.login(username='admin4', password='Admin1234!')
        self.product = Product.objects.create(
            code='P002', name='Laptop', purchase_price='500', sale_price='700'
        )
        self.inventory = Inventory.objects.create(product=self.product, quantity=10, minimum_stock=2)

    def test_sale_list(self):
        resp = self.client.get(reverse('sale_list'))
        self.assertEqual(resp.status_code, 200)

    def test_create_sale_deducts_stock(self):
        resp = self.client.post(reverse('sale_create'), {
            'customer_name': 'Ana López',
            'status': 'completed',
            'notes': '',
            'details-TOTAL_FORMS': '1',
            'details-INITIAL_FORMS': '0',
            'details-MIN_NUM_FORMS': '1',
            'details-MAX_NUM_FORMS': '1000',
            'details-0-product': self.product.pk,
            'details-0-quantity': '3',
            'details-0-unit_price': '700.00',
        })
        self.assertEqual(Sale.objects.count(), 1)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)  # 10 - 3

    def test_sale_total_calculation(self):
        sale = Sale.objects.create(salesperson=self.admin, customer_name='Test', status=Sale.COMPLETED)
        SaleDetail.objects.create(sale=sale, product=self.product, quantity=2, unit_price='700.00')
        SaleDetail.objects.create(sale=sale, product=self.product, quantity=1, unit_price='500.00')
        self.assertEqual(sale.total, 1900)

    def test_cancel_sale_restores_stock(self):
        # Create sale
        sale = Sale.objects.create(salesperson=self.admin, customer_name='Test', status=Sale.COMPLETED)
        SaleDetail.objects.create(sale=sale, product=self.product, quantity=2, unit_price='700.00')
        self.inventory.quantity -= 2
        self.inventory.save()
        InventoryMovement.objects.create(
            inventory=self.inventory, movement_type=InventoryMovement.OUT,
            quantity=2, created_by=self.admin
        )
        # Cancel sale
        resp = self.client.post(reverse('sale_cancel', args=[sale.pk]))
        self.inventory.refresh_from_db()
        sale.refresh_from_db()
        self.assertEqual(sale.status, Sale.CANCELLED)
        self.assertEqual(self.inventory.quantity, 10)  # restored
