from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from .models import Sale, SaleDetail
from .forms import SaleForm, SaleDetailFormSet
from inventory.models import Inventory, InventoryMovement


@method_decorator(login_required, name='dispatch')
class SaleListView(View):
    def get(self, request):
        sales = Sale.objects.select_related('salesperson').prefetch_related('details').all()
        return render(request, 'sales/sale_list.html', {'sales': sales})


@method_decorator(login_required, name='dispatch')
class SaleCreateView(View):
    def get(self, request):
        form = SaleForm()
        formset = SaleDetailFormSet()
        return render(request, 'sales/sale_form.html', {
            'form': form, 'formset': formset, 'title': 'Nueva Venta',
        })

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save(commit=False)
                sale.salesperson = request.user
                sale.save()
                details = formset.save(commit=False)
                for detail in details:
                    detail.sale = sale
                    # Deduct stock
                    inv = Inventory.objects.select_for_update().get(product=detail.product)
                    if inv.quantity < detail.quantity:
                        messages.error(
                            request,
                            f'Stock insuficiente para {detail.product.name}. Disponible: {inv.quantity}.',
                        )
                        transaction.set_rollback(True)
                        return render(request, 'sales/sale_form.html', {
                            'form': form, 'formset': formset, 'title': 'Nueva Venta',
                        })
                    detail.save()
                    inv.quantity -= detail.quantity
                    inv.save()
                    InventoryMovement.objects.create(
                        inventory=inv,
                        movement_type=InventoryMovement.OUT,
                        quantity=detail.quantity,
                        reason=f'Venta #{sale.pk}',
                        created_by=request.user,
                    )
                for obj in formset.deleted_objects:
                    obj.delete()
            messages.success(request, f'Venta #{sale.pk} registrada exitosamente.')
            return redirect('sale_detail', pk=sale.pk)
        return render(request, 'sales/sale_form.html', {
            'form': form, 'formset': formset, 'title': 'Nueva Venta',
        })


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('details__product'), pk=pk)
    return render(request, 'sales/sale_detail.html', {'sale': sale})


@login_required
def sale_cancel(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tiene permisos para cancelar ventas.')
        return redirect('sale_list')
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST' and sale.status != Sale.CANCELLED:
        with transaction.atomic():
            for detail in sale.details.all():
                inv = Inventory.objects.select_for_update().get(product=detail.product)
                inv.quantity += detail.quantity
                inv.save()
                InventoryMovement.objects.create(
                    inventory=inv,
                    movement_type=InventoryMovement.IN,
                    quantity=detail.quantity,
                    reason=f'Cancelación venta #{sale.pk}',
                    created_by=request.user,
                )
            sale.status = Sale.CANCELLED
            sale.save()
        messages.success(request, f'Venta #{sale.pk} cancelada y stock restaurado.')
        return redirect('sale_list')
    return render(request, 'sales/sale_confirm_cancel.html', {'sale': sale})
