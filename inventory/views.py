from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from .models import Inventory, InventoryMovement
from .forms import InventoryMovementForm
from products.models import Product


@method_decorator(login_required, name='dispatch')
class InventoryListView(View):
    def get(self, request):
        inventories = Inventory.objects.select_related('product').all()
        return render(request, 'inventory/inventory_list.html', {'inventories': inventories})


@method_decorator(login_required, name='dispatch')
class InventoryAdjustView(View):
    """Register a stock movement (entry, exit, or manual adjustment)."""

    def get(self, request, pk):
        inventory = get_object_or_404(Inventory, pk=pk)
        form = InventoryMovementForm()
        return render(request, 'inventory/inventory_adjust.html', {
            'inventory': inventory,
            'form': form,
        })

    def post(self, request, pk):
        inventory = get_object_or_404(Inventory, pk=pk)
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.inventory = inventory
            movement.created_by = request.user
            movement.save()

            # Update stock
            qty = form.cleaned_data['quantity']
            mtype = form.cleaned_data['movement_type']
            if mtype == InventoryMovement.IN:
                inventory.quantity += qty
            elif mtype == InventoryMovement.OUT:
                if inventory.quantity < qty:
                    messages.error(request, 'Stock insuficiente para realizar la salida.')
                    return render(request, 'inventory/inventory_adjust.html', {
                        'inventory': inventory, 'form': form,
                    })
                inventory.quantity -= qty
            else:  # adjustment
                inventory.quantity = qty
            inventory.save()
            messages.success(request, 'Movimiento registrado correctamente.')
            return redirect('inventory_list')
        return render(request, 'inventory/inventory_adjust.html', {
            'inventory': inventory, 'form': form,
        })


@login_required
def inventory_movements(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    movements = inventory.movements.select_related('created_by').order_by('-created_at')
    return render(request, 'inventory/inventory_movements.html', {
        'inventory': inventory, 'movements': movements,
    })
