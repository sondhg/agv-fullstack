from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from rest_framework.generics import ListAPIView
from .services.algorithm_1 import TaskDispatcher
from .services.algorithm_3 import DeadlockResolver
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
                # Reset all AGV state fields to their default values,
                # except for preferred_parking_node and agv_id
                agv.motion_state = AGV_STATE_IDLE
                agv.active_schedule = None
                agv.spare_flag = False
                agv.spare_points = dict()  # Reset to default empty dict
                agv.current_node = agv.preferred_parking_node  # Set to preferred parking node as default
                agv.next_node = None
                agv.reserved_node = None
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
                    # Reset all AGV state fields to their default values,
                    # except for preferred_parking_node and agv_id
                    agv.motion_state = AGV_STATE_IDLE
                    agv.active_schedule = None
                    agv.spare_flag = False
                    agv.spare_points = dict()  # Reset to default empty dict
                    agv.current_node = agv.preferred_parking_node  # Set to preferred parking node as default
                    agv.next_node = None
                    agv.reserved_node = None
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


class DeadlockDetectionView(APIView):
    """
    API endpoint to detect and resolve deadlocks in the AGV system.
    Implements Algorithm 3: Deadlock Resolution of the Central Controller.
    """
    
    def get(self, request):
        """
        Detects and resolves deadlocks in the system.
        
        This endpoint checks for head-on and loop deadlocks among AGVs in the
        waiting state and resolves them by moving AGVs with spare points.
        
        Response format:
        {
            "success": bool,         # Whether the operation was successful
            "message": str,          # Description of the operation result
            "deadlocks_resolved": int,  # Number of deadlocks resolved
            "agvs_moved": List[int]  # List of AGV IDs that were moved to resolve deadlocks
        }
        """
        try:
            # Initialize the deadlock resolver
            resolver = DeadlockResolver()
            
            # Detect and resolve deadlocks
            result = resolver.detect_and_resolve_deadlocks()
            
            # Return the result
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error during deadlock detection: {str(e)}",
                    "deadlocks_resolved": 0,
                    "agvs_moved": []
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
