from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateOrderView, BulkDeleteOrdersView, ListOrdersView, DeleteOrderView

router = DefaultRouter()
# # localhost:8000/api/orders/
# router.register(r'orders', CreateOrderView, basename='order')

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path('bulk-delete/', BulkDeleteOrdersView.as_view(), name='bulk_delete_orders'),
    path("", ListOrdersView.as_view(),
         name="list_orders"),  # Add this line
    path("<int:order_id>/delete/",
         DeleteOrderView.as_view(), name="delete_order"),
]
