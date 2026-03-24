from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleDetail


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'status', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'customer_name': 'Cliente',
            'status': 'Estado',
            'notes': 'Notas',
        }


class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'product': 'Producto',
            'quantity': 'Cantidad',
            'unit_price': 'Precio unitario',
        }


SaleDetailFormSet = inlineformset_factory(
    Sale,
    SaleDetail,
    form=SaleDetailForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
