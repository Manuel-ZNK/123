from django.db import models
from products.models import Product
from accounts.models import User


class Inventory(models.Model):
    """Current stock level for a product."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Producto',
    )
    quantity = models.IntegerField(default=0, verbose_name='Cantidad en stock')
    minimum_stock = models.IntegerField(
        default=5, verbose_name='Stock mínimo'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        ordering = ['product__name']

    def __str__(self):
        return f'{self.product.name} – {self.quantity} uds.'

    @property
    def is_low_stock(self):
        """Return True when quantity is below (not equal to) the minimum_stock threshold.
        
        minimum_stock represents the lowest *acceptable* quantity; reaching it
        triggers a low-stock warning so staff can reorder before running out.
        """
        return self.quantity < self.minimum_stock


class InventoryMovement(models.Model):
    """Records every stock in/out movement."""

    IN = 'in'
    OUT = 'out'
    ADJUSTMENT = 'adjustment'
    MOVEMENT_TYPES = [
        (IN, 'Entrada'),
        (OUT, 'Salida'),
        (ADJUSTMENT, 'Ajuste'),
    ]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Inventario',
    )
    movement_type = models.CharField(
        max_length=20, choices=MOVEMENT_TYPES, verbose_name='Tipo de movimiento'
    )
    quantity = models.IntegerField(verbose_name='Cantidad')
    reason = models.CharField(max_length=255, blank=True, verbose_name='Motivo')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_movements',
        verbose_name='Realizado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.get_movement_type_display()} – '
            f'{self.inventory.product.name} x{self.quantity}'
        )
