from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta
from sales.models import Sale, SaleDetail
from inventory.models import Inventory
from products.models import Product


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_sales_today = Sale.objects.filter(
        created_at__date=today, status=Sale.COMPLETED
    ).count()
    revenue_today = (
        SaleDetail.objects.filter(
            sale__created_at__date=today, sale__status=Sale.COMPLETED
        ).aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0
    )
    revenue_month = (
        SaleDetail.objects.filter(
            sale__created_at__date__gte=month_start, sale__status=Sale.COMPLETED
        ).aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0
    )
    low_stock = Inventory.objects.filter(
        quantity__lte=F('minimum_stock')
    ).select_related('product').count()
    total_products = Product.objects.filter(is_active=True).count()
    recent_sales = Sale.objects.select_related('salesperson').prefetch_related('details')[:5]

    context = {
        'total_sales_today': total_sales_today,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'low_stock': low_stock,
        'total_products': total_products,
        'recent_sales': recent_sales,
        'today': today,
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sales = Sale.objects.select_related('salesperson').prefetch_related('details')

    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    total_revenue = sum(s.total for s in sales if s.status == Sale.COMPLETED)

    return render(request, 'reports/sales_report.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required
def inventory_report(request):
    inventories = Inventory.objects.select_related('product__category').order_by('product__name')
    low_stock = [inv for inv in inventories if inv.is_low_stock]
    return render(request, 'reports/inventory_report.html', {
        'inventories': inventories,
        'low_stock': low_stock,
    })
