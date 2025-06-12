from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Agv
from .serializers import AGVSerializer
from django.db import transaction
import schedule
import datetime
from django.conf import settings
from order_data.models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_order_assignment_notification(order_id, agv_id, message):
    """
    Send order assignment notification through WebSocket.

    Args:
        order_id: The ID of the assigned order
        agv_id: The ID of the AGV that received the order
        message: The notification message to display
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "agv_group",
            {
                "type": "agv_message",
                "message": {
                    "type": "order_assignment_notification",
                    "data": {
                        "order_id": order_id,
                        "agv_id": agv_id,
                        "message": message,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                }
            }
        )
    except Exception as e:
        print(f"Error sending order assignment notification: {str(e)}")


class ListAGVsView(ListAPIView):
    queryset = Agv.objects.all()
    serializer_class = AGVSerializer


class CreateAGVView(APIView):
    def post(self, request):
        if isinstance(request.data, list):
            # Handle multiple objects
            serializer = AGVSerializer(data=request.data, many=True)
        else:
            # Handle single object
            serializer = AGVSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAGVView(APIView):
    def delete(self, request, agv_id):
        try:
            agv = Agv.objects.get(agv_id=agv_id)
            agv.delete()
            return Response(
                {"message": f"AGV {agv_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Agv.DoesNotExist:
            return Response(
                {"error": f"AGV {agv_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BulkDeleteAGVsView(APIView):
    def delete(self, request):
        try:
            agv_ids = request.data.get("agv_ids", [])
            if not agv_ids:
                return Response(
                    {"error": "No AGV IDs provided for deletion."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count, _ = Agv.objects.filter(
                agv_id__in=agv_ids).delete()
            return Response(
                {"message": f"{deleted_count} AGVs deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during bulk deletion: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DispatchOrdersToAGVsView(APIView):
    """
    API endpoint to schedule orders to be assigned to available AGVs at their specified times.
    This replaces the functionality previously in the schedule_generate app.
    """

    def __init__(self):
        super().__init__()
        from .services.order_scheduler import OrderSchedulerService, OrderAssignmentService
        self.scheduler_service = OrderSchedulerService()
        self.assignment_service = OrderAssignmentService()

    def post(self, request):
        """
        Schedule orders to be assigned to idle AGVs at their specified start_time and order_date.

        Returns:
            Response: Information about scheduled orders.
        """
        try:
            # Get the algorithm parameter (defaults to dijkstra)
            algorithm = request.data.get("algorithm", "dijkstra")

            # Get all unassigned orders with their scheduling information
            unassigned_orders = self.scheduler_service.get_unassigned_orders()

            if not unassigned_orders.exists():
                return self._create_no_orders_response()

            # Clear any existing scheduled jobs to avoid duplicates
            schedule.clear()

            # Process orders for scheduling or immediate assignment
            scheduled_orders, immediate_orders = self.scheduler_service.process_orders_for_scheduling(
                unassigned_orders, algorithm, self.assignment_service.assign_single_order
            )

            # Start scheduler if needed
            self.scheduler_service.start_scheduler_if_needed(scheduled_orders)

            return self._create_success_response(scheduled_orders, immediate_orders)

        except Exception as e:
            return self._create_error_response(e)

    def _create_no_orders_response(self):
        """Create response for when no unassigned orders are available."""
        return Response(
            {
                "success": False,
                "message": "No unassigned orders available to schedule."
            },
            status=status.HTTP_200_OK,
        )

    def _create_success_response(self, scheduled_orders, immediate_orders):
        """Create success response with order scheduling results."""
        total_processed = len(scheduled_orders) + len(immediate_orders)

        return Response(
            {
                "success": True,
                "message": f"Successfully scheduled {len(scheduled_orders)} orders and immediately assigned {len(immediate_orders)} orders",
                "scheduled_orders": scheduled_orders,
                "immediate_orders": immediate_orders,
                "total_processed": total_processed
            },
            status=status.HTTP_200_OK,
        )

    def _create_error_response(self, exception):
        """Create error response with exception details."""
        import traceback
        traceback_str = traceback.format_exc()

        return Response(
            {
                "success": False,
                "message": f"Error scheduling orders: {str(exception)}",
                "details": traceback_str
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ResetAGVsView(APIView):
    """
    API endpoint to reset all fields of all AGV records to their default values,
    except for agv_id and preferred_parking_node.
    """

    @transaction.atomic
    def post(self, request):
        try:
            # Get all AGVs
            agvs = Agv.objects.all()

            if not agvs.exists():
                return Response(
                    {"success": False, "message": "No AGVs found to reset."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            reset_count = 0

            # Reset each AGV
            for agv in agvs:
                # Store the fields we want to keep
                agv_id = agv.agv_id
                preferred_parking_node = agv.preferred_parking_node

                # Reset all state fields
                agv.current_node = None
                agv.next_node = None
                agv.reserved_node = None
                agv.motion_state = Agv.IDLE
                agv.spare_flag = False
                agv.backup_nodes = {}
                agv.initial_path = []
                agv.remaining_path = []
                agv.common_nodes = []
                agv.adjacent_common_nodes = []
                agv.active_order = None
                agv.previous_node = None
                agv.direction_change = Agv.STAY_STILL

                # Save the changes
                agv.save(update_fields=[
                    'current_node', 'next_node', 'reserved_node', 'motion_state',
                    'spare_flag', 'backup_nodes', 'initial_path', 'remaining_path',
                    'common_nodes', 'adjacent_common_nodes', 'active_order', 'previous_node', 'direction_change'
                ])

                reset_count += 1

            return Response(
                {
                    "success": True,
                    "message": f"Successfully reset {reset_count} AGVs to their default state."
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response(
                {
                    "success": False,
                    "message": f"Error resetting AGVs: {str(e)}",
                    "details": traceback_str
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,)


class ScheduleOrderHellosView(APIView):
    """
    API endpoint to schedule MQTT messages based on their order start_time and order_date.
    When the frontend sends a GET request to this endpoint, it will:
    1. Get list of all AGVs with active_order_info
    2. Schedule "Hey" messages to be sent to MQTT topic "agvhello/{agv_id}" at the time that matches start_time and order_date
    """

    def __init__(self):
        super().__init__()
        from .services.hello_scheduler import HelloSchedulerService
        self.hello_scheduler_service = HelloSchedulerService()

    def get(self, request):
        """
        Schedule MQTT hello messages for AGVs with active orders.

        Returns:
            Response: Information about scheduled hello messages.
        """
        try:
            # Get all AGVs with active orders
            agvs_with_orders = self.hello_scheduler_service.get_agvs_with_active_orders()

            # Clear any existing scheduled jobs to avoid duplicates
            schedule.clear()

            # Process AGVs for hello message scheduling
            scheduled_messages = self.hello_scheduler_service.process_agvs_for_hello_scheduling(
                agvs_with_orders)

            # Start scheduler if needed
            self.hello_scheduler_service.start_scheduler_if_needed(
                scheduled_messages)

            return self._create_success_response(scheduled_messages)

        except Exception as e:
            return self._create_error_response(e)

    def _create_success_response(self, scheduled_messages):
        """Create success response with hello message scheduling results."""
        return Response(
            {
                "success": True,
                "message": f"Scheduled MQTT hello messages for {len(scheduled_messages)} AGVs",
                "scheduled_messages": scheduled_messages
            },
            status=status.HTTP_200_OK,
        )

    def _create_error_response(self, exception):
        """Create error response with exception details."""
        import traceback
        traceback_str = traceback.format_exc()

        return Response(
            {
                "success": False,
                "message": f"Error scheduling hello messages: {str(exception)}",
                "details": traceback_str
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
