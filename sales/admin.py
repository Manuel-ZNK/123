from django.contrib import admin
from .models import Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'salesperson', 'customer_name', 'status', 'created_at']
    list_filter = ['status']
    inlines = [SaleDetailInline]
