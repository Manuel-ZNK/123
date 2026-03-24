from django.urls import path
from . import views

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/cancel/', views.sale_cancel, name='sale_cancel'),
]
