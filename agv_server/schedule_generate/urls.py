from django.urls import path
from .views import GenerateSchedulesView, ListSchedulesView, DeleteScheduleView

urlpatterns = [
    path("generate/", GenerateSchedulesView.as_view(), name="generate_schedules"),
    path("", ListSchedulesView.as_view(),
         name="list_schedules"),  # Add this line
    path("<int:schedule_id>/delete/",
         DeleteScheduleView.as_view(), name="delete_schedule"),
]
