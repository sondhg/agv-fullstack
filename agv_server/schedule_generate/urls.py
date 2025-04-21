from django.urls import path
from .views import GenerateSchedulesView, ListSchedulesView, DeleteScheduleView, BulkDeleteSchedulesView, DeadlockDetectionView

urlpatterns = [
    path("generate/", GenerateSchedulesView.as_view(), name="generate_schedules"),
    path("get/", ListSchedulesView.as_view(), name="list_schedules"),
    path("delete/<int:schedule_id>/", DeleteScheduleView.as_view(), name="delete_schedule"),
    path('bulk-delete/', BulkDeleteSchedulesView.as_view(), name='bulk_delete_schedules'),
    path('detect-deadlocks/', DeadlockDetectionView.as_view(), name='detect_deadlocks'),
]
