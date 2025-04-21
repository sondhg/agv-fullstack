from django.urls import path
from .views import CreateAGVView, ListAGVsView, DeleteAGVView, BulkDeleteAGVsView, UpdateAGVPositionView

urlpatterns = [
    path("get/", ListAGVsView.as_view(), name="list_agvs"),
    path('create/', CreateAGVView.as_view(), name='create_agv'),
    path("delete/<int:agv_id>/", DeleteAGVView.as_view(), name="delete_agv"),
    path('bulk-delete/', BulkDeleteAGVsView.as_view(), name='bulk_delete_agvs'),
    path('update-position/', UpdateAGVPositionView.as_view(), name='update_agv_position'),
]