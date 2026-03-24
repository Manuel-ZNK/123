from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from inventory.models import Inventory


@method_decorator(login_required, name='dispatch')
class ProductListView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        products = Product.objects.select_related('category').all()
        if query:
            products = products.filter(name__icontains=query) | products.filter(code__icontains=query)
        return render(request, 'products/product_list.html', {'products': products, 'query': query})


@method_decorator(login_required, name='dispatch')
class ProductCreateView(View):
    def get(self, request):
        if not request.user.is_admin():
            return redirect('product_list')
        form = ProductForm()
        return render(request, 'products/product_form.html', {'form': form, 'title': 'Nuevo Producto'})

    def post(self, request):
        if not request.user.is_admin():
            return redirect('product_list')
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            Inventory.objects.get_or_create(product=product, defaults={'quantity': 0})
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('product_list')
        return render(request, 'products/product_form.html', {'form': form, 'title': 'Nuevo Producto'})


@method_decorator(login_required, name='dispatch')
class ProductEditView(View):
    def get(self, request, pk):
        if not request.user.is_admin():
            return redirect('product_list')
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        return render(request, 'products/product_form.html', {'form': form, 'title': 'Editar Producto', 'object': product})

    def post(self, request, pk):
        if not request.user.is_admin():
            return redirect('product_list')
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('product_list')
        return render(request, 'products/product_form.html', {'form': form, 'title': 'Editar Producto', 'object': product})


@login_required
def product_delete(request, pk):
    if not request.user.is_admin():
        return redirect('product_list')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'object': product})


# ─── Categories ───────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class CategoryListView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'products/category_list.html', {'categories': categories})


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(View):
    def get(self, request):
        if not request.user.is_admin():
            return redirect('category_list')
        form = CategoryForm()
        return render(request, 'products/category_form.html', {'form': form, 'title': 'Nueva Categoría'})

    def post(self, request):
        if not request.user.is_admin():
            return redirect('category_list')
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('category_list')
        return render(request, 'products/category_form.html', {'form': form, 'title': 'Nueva Categoría'})


@login_required
def category_delete(request, pk):
    if not request.user.is_admin():
        return redirect('category_list')
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada.')
        return redirect('category_list')
    return render(request, 'products/category_confirm_delete.html', {'object': category})
