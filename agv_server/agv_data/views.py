from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Agv
from .serializers import AGVSerializer
from .services.algorithm1 import TaskDispatcher
from .constants import SuccessMessages
from django.db import transaction
import schedule
import time
import datetime
from . import mqtt
from django.conf import settings
import threading


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
    API endpoint to process orders and assign them to available AGVs.
    This replaces the functionality previously in the schedule_generate app.
    """

    def post(self, request):
        """
        Process available orders and assign them to idle AGVs.

        Returns:
            Response: Information about processed orders and assigned AGVs.
        """
        try:
            # Initialize the task dispatcher (Algorithm 1)
            dispatcher = TaskDispatcher()

            # Dispatch tasks (orders) to available AGVs
            processed_orders = dispatcher.dispatch_tasks()

            if processed_orders:
                return Response(
                    {
                        "success": True,
                        "message": SuccessMessages.ORDERS_PROCESSED.format(len(processed_orders)),
                        "processed_orders": processed_orders
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": "No orders were processed. Check that you have available orders and idle AGVs."
                    },
                    status=status.HTTP_200_OK,
                )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response(
                {
                    "success": False,
                    "message": f"Error processing orders: {str(e)}",
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
                agv.spare_points = {}
                agv.initial_path = []
                agv.remaining_path = []
                agv.cp = []
                agv.scp = []
                agv.active_order = None
                agv.previous_node = None
                agv.direction_change = Agv.STAY_STILL

                # Save the changes
                agv.save(update_fields=[
                    'current_node', 'next_node', 'reserved_node', 'motion_state',
                    'spare_flag', 'spare_points', 'initial_path', 'remaining_path',
                    'cp', 'scp', 'active_order', 'previous_node', 'direction_change'
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


def send_agv_hello_message(agv_id):
    """
    Send a "Hey" message to the MQTT broker topic agvhello/{agv_id}.

    Args:
        agv_id: The ID of the AGV to send the hello message to
    """
    try:
        topic = f"{settings.MQTT_TOPIC_AGVHELLO}/{agv_id}"

        frame = bytearray()
        HELLO_FRAME = 0x01
        frame.append(HELLO_FRAME)

        message = bytes(frame)

        # Use the global MQTT client from the mqtt module
        mqtt.client.publish(topic, message)
        print(
            f"Successfully sent MQTT message {message} to topic '{topic}' for AGV {agv_id}")

    except Exception as e:
        print(f"Error sending MQTT hello message to AGV {agv_id}: {str(e)}")


class ScheduleOrderHellosView(APIView):
    """
    API endpoint to schedule MQTT messages based on their order start_time and order_date.
    When the frontend sends a GET request to this endpoint, it will:
    1. Get list of all AGVs with active_order_info
    2. Schedule "Hey" messages to be sent to MQTT topic "agvhello/{agv_id}" at the time that matches start_time and order_date
    """

    # Class variable to track if scheduler is running
    _scheduler_running = False
    _scheduler_thread = None

    @classmethod
    def _run_scheduler(cls):
        """Run the scheduler in a background thread"""
        cls._scheduler_running = True
        while cls._scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        print("Scheduler thread stopped")

    def get(self, request):
        # Get all AGVs with active orders
        agvs_with_orders = Agv.objects.filter(
            active_order__isnull=False)

        # Clear any existing scheduled jobs to avoid duplicates
        schedule.clear()

        scheduled_messages = []

        for agv in agvs_with_orders:
            agv_id = agv.agv_id
            # Get the active order for this AGV
            active_order = agv.active_order
            # Get the order date and start time
            order_date = active_order.order_date
            # Combine date and time to create a datetime object
            start_time = active_order.start_time
            schedule_datetime = datetime.datetime.combine(
                order_date, start_time)

            # Only schedule if the time is in the future
            now = datetime.datetime.now()
            if schedule_datetime > now:
                # Create a closure to capture the agv_id correctly
                def create_hello_function(agv_id_val):
                    def send_hello():
                        send_agv_hello_message(agv_id_val)
                        # Remove this job after it runs once
                        return schedule.CancelJob
                    return send_hello

                # Schedule at specific time (hour, minute, second) rather than with a delay
                job = schedule.every().day.at(start_time.strftime(
                    "%H:%M:%S")).do(create_hello_function(agv_id))
                job.tag(f"agv_{agv_id}")

                scheduled_messages.append({
                    "agv_id": agv_id,
                    "scheduled_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "seconds_from_now": (schedule_datetime - now).total_seconds()})
                print(
                    f"Scheduled MQTT message for AGV {agv_id} at {start_time.strftime('%H:%M:%S')}")
            else:
                # If the time is in the past, send MQTT message immediately
                send_agv_hello_message(agv_id)
                print(
                    f"Sent immediate MQTT hello message to AGV {agv_id} (scheduled time already passed)")

        # Start the scheduler thread if not already running

        if not ScheduleOrderHellosView._scheduler_running and scheduled_messages:
            if ScheduleOrderHellosView._scheduler_thread and ScheduleOrderHellosView._scheduler_thread.is_alive():
                # Reuse existing thread
                pass
            else:                # Create a new thread
                ScheduleOrderHellosView._scheduler_thread = threading.Thread(
                    target=ScheduleOrderHellosView._run_scheduler,
                    daemon=True,
                    name="scheduler_thread"
                )
                ScheduleOrderHellosView._scheduler_thread.start()

        return Response(
            {
                "success": True,
                "message": f"Scheduled MQTT hello messages for {len(scheduled_messages)} AGVs",
                "scheduled_messages": scheduled_messages
            },
            status=status.HTTP_200_OK,
        )
