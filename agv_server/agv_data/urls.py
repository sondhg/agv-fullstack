from django.urls import path
from .views import (
    CreateAGVView,
    ListAGVsView,
    DeleteAGVView,
    BulkDeleteAGVsView,
    DispatchOrdersToAGVsView,
    ResetAGVsView,
    ScheduleOrderHellosView
)

urlpatterns = [
    path("get/", ListAGVsView.as_view(), name="list_agvs"),
    path('create/', CreateAGVView.as_view(), name='create_agv'),
    path("delete/<int:agv_id>/", DeleteAGVView.as_view(), name="delete_agv"),
    path('bulk-delete/', BulkDeleteAGVsView.as_view(), name='bulk_delete_agvs'),
    path('reset/', ResetAGVsView.as_view(), name='reset_agvs'),
    path('dispatch-orders-to-agvs/', DispatchOrdersToAGVsView.as_view(),
         name='dispatch_orders_to_agvs'),
    path('schedule-hello-messages/', ScheduleOrderHellosView.as_view(),
         name='schedule_hello_messages'),
]
