from django.contrib import admin
from .models import Inventory, InventoryMovement


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'minimum_stock', 'updated_at']
    search_fields = ['product__name', 'product__code']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory', 'movement_type', 'quantity', 'reason', 'created_by', 'created_at']
    list_filter = ['movement_type']
