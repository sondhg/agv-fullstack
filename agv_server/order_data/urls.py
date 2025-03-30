from django.urls import path
from .views import CreateOrderView, ListOrdersView, DeleteOrderView, BulkDeleteOrdersView


urlpatterns = [
    path("get/", ListOrdersView.as_view(),
         name="list_orders"),
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path("delete/<int:order_id>/",
         DeleteOrderView.as_view(), name="delete_order"),
    path('bulk-delete/', BulkDeleteOrdersView.as_view(), name='bulk_delete_orders'),
]
