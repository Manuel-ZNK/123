from django.db import models
from django.db.models import Sum, F
from accounts.models import User
from products.models import Product


class Sale(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (COMPLETED, 'Completada'),
        (CANCELLED, 'Cancelada'),
    ]

    salesperson = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
        verbose_name='Vendedor',
    )
    customer_name = models.CharField(
        max_length=200, blank=True, verbose_name='Cliente'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=COMPLETED,
        verbose_name='Estado',
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']

    def __str__(self):
        return f'Venta #{self.pk} – {self.created_at.strftime("%d/%m/%Y")}'

    @property
    def total(self):
        result = self.details.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total']
        return result or 0


class SaleDetail(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='Venta',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_details',
        verbose_name='Producto',
    )
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Precio unitario'
    )

    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price
