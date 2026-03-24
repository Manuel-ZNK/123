from django import forms
from .models import Inventory, InventoryMovement


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity', 'minimum_stock']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity': 'Cantidad en stock',
            'minimum_stock': 'Stock mínimo',
        }


class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = ['movement_type', 'quantity', 'reason']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'movement_type': 'Tipo de movimiento',
            'quantity': 'Cantidad',
            'reason': 'Motivo',
        }
