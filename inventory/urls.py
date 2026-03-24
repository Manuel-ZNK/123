from django.urls import path
from . import views

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='inventory_list'),
    path('<int:pk>/adjust/', views.InventoryAdjustView.as_view(), name='inventory_adjust'),
    path('<int:pk>/movements/', views.inventory_movements, name='inventory_movements'),
]
