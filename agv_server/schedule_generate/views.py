from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from rest_framework.generics import ListAPIView
from .services.algorithm_1 import TaskDispatcher
from .constants import ErrorMessages, SuccessMessages, DefaultValues
from agv_data.models import AGV_STATE_IDLE


class GenerateSchedulesView(APIView):
    def post(self, request):
        try:
            # Get the algorithm choice from the request body
            algorithm = request.data.get(
                "algorithm", DefaultValues.DEFAULT_ALGORITHM).lower()

            # Use TaskDispatcher instead of ScheduleService to generate schedules
            dispatcher = TaskDispatcher()
            schedules = dispatcher.dispatch_tasks(algorithm)

            if not schedules:
                return Response(
                    {"error": ErrorMessages.NO_SCHEDULES},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "message": SuccessMessages.SCHEDULES_GENERATED,
                    "schedules": schedules
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during schedule generation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListSchedulesView(ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class DeleteScheduleView(APIView):
    def delete(self, request, schedule_id):
        try:
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            # Get associated AGV before deleting the schedule
            agv = schedule.assigned_agv
            if agv:
                # Reset all AGV state fields
                agv.motion_state = AGV_STATE_IDLE
                agv.active_schedule = None
                agv.spare_flag = False
                agv.in_sequential_shared_points = False
                agv.is_deadlocked = False
                agv.last_spare_point = None
                agv.save()
            schedule.delete()
            return Response(
                {"message": SuccessMessages.SCHEDULE_DELETED.format(
                    schedule_id)},
                status=status.HTTP_200_OK,
            )
        except Schedule.DoesNotExist:
            return Response(
                {"error": f"Schedule {schedule_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BulkDeleteSchedulesView(APIView):
    def delete(self, request):
        try:
            schedule_ids = request.data.get("schedule_ids", [])
            if not schedule_ids:
                return Response(
                    {"error": ErrorMessages.BULK_DELETE_NO_IDS},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get all schedules with their assigned AGVs that will be deleted
            schedules = Schedule.objects.filter(schedule_id__in=schedule_ids)

            # Reset AGV states for all affected AGVs
            for schedule in schedules:
                agv = schedule.assigned_agv
                if agv:
                    agv.motion_state = AGV_STATE_IDLE
                    agv.active_schedule = None
                    agv.spare_flag = False
                    agv.in_sequential_shared_points = False
                    agv.is_deadlocked = False
                    agv.last_spare_point = None
                    agv.save()

            # Now delete the schedules
            deleted_count = schedules.delete()[0]
            return Response(
                {"message": SuccessMessages.SCHEDULES_DELETED.format(
                    deleted_count)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during bulk deletion: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
