from .tasks.deadlock_detector import DeadlockDetector
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from order_data.models import Order
from rest_framework.generics import ListAPIView
from map_data.models import Direction, Connection
import json
from .pathfinding.factory import PathfindingFactory
from .pathfinding.cp_scp_calculator import CpScpCalculator
from .pathfinding.sp_calculator import SpCalculator
from .pathfinding.traveling_info_updater import TravelingInfoUpdater
from .pathfinding.movement_conditions import MovementConditions
from .services.schedule_service import ScheduleService
from .services.deadlock_service import DeadlockService
from .constants import ErrorMessages, SuccessMessages, DefaultValues


class GenerateSchedulesView(APIView):
    def post(self, request):
        try:
            # Get the algorithm choice from the request body
            algorithm = request.data.get(
                "algorithm", DefaultValues.DEFAULT_ALGORITHM).lower()

            # Generate schedules using the service
            schedules = ScheduleService.generate_schedules(algorithm)

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

            deleted_count, _ = Schedule.objects.filter(
                schedule_id__in=schedule_ids).delete()
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


class UpdateScheduleView(APIView):
    def put(self, request, schedule_id):
        try:
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            data = request.data

            current_point = data.get("current_point")
            next_point = data.get("next_point")

            if current_point is not None and next_point is not None:
                # Update schedule state
                schedule = ScheduleService.update_schedule_state(
                    schedule, current_point, next_point
                )

                # Check for deadlocks
                resolved, deadlocks = DeadlockService.check_and_resolve_deadlocks()

                if deadlocks:
                    return Response(
                        {
                            "message": "Deadlock detected",
                            "deadlocks": deadlocks,
                            "resolved": resolved,
                            "schedule": ScheduleSerializer(schedule).data
                        },
                        status=status.HTTP_409_CONFLICT if not resolved else status.HTTP_200_OK
                    )

                return Response(
                    {
                        "message": "Schedule updated successfully",
                        "schedule": ScheduleSerializer(schedule).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Missing current_point or next_point in request"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Schedule.DoesNotExist:
            return Response(
                {"error": f"Schedule {schedule_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while updating schedule: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
