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
from order_data.models import Order


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
        print("Order scheduler thread stopped")

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
            unassigned_orders = Order.objects.filter(active_agv__isnull=True)
            
            if not unassigned_orders.exists():
                return Response(
                    {
                        "success": False,
                        "message": "No unassigned orders available to schedule."
                    },
                    status=status.HTTP_200_OK,
                )

            # Clear any existing scheduled jobs to avoid duplicates
            schedule.clear()

            scheduled_orders = []
            immediate_orders = []

            for order in unassigned_orders:
                # Check if there's an available AGV for this order's parking node
                available_agv = Agv.objects.filter(
                    motion_state=Agv.IDLE,
                    preferred_parking_node=order.parking_node,
                    active_order__isnull=True
                ).first()

                if not available_agv:
                    print(f"No available AGV for order {order.order_id} at parking node {order.parking_node}")
                    continue

                # Combine order date and start time to create a datetime object
                schedule_datetime = datetime.datetime.combine(order.order_date, order.start_time)
                now = datetime.datetime.now()

                if schedule_datetime > now:
                    # Schedule order for future assignment
                    def create_assignment_function(order_id_val, algorithm_val):
                        def assign_order():
                            self._assign_single_order(order_id_val, algorithm_val)
                            return schedule.CancelJob  # Remove job after execution
                        return assign_order

                    # Schedule at specific time
                    job = schedule.every().day.at(order.start_time.strftime("%H:%M:%S")).do(
                        create_assignment_function(order.order_id, algorithm)
                    )
                    job.tag(f"order_{order.order_id}")

                    scheduled_orders.append({
                        "order_id": order.order_id,
                        "agv_id": available_agv.agv_id,
                        "parking_node": order.parking_node,
                        "scheduled_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "seconds_from_now": (schedule_datetime - now).total_seconds()
                    })
                    print(f"Scheduled order {order.order_id} for AGV {available_agv.agv_id} at {order.start_time.strftime('%H:%M:%S')}")
                else:
                    # Assign order immediately if scheduled time has passed
                    success = self._assign_single_order(order.order_id, algorithm)
                    if success:
                        immediate_orders.append({
                            "order_id": order.order_id,
                            "agv_id": available_agv.agv_id,
                            "parking_node": order.parking_node,
                            "status": "assigned_immediately"
                        })
                        print(f"Assigned order {order.order_id} to AGV {available_agv.agv_id} immediately (scheduled time already passed)")

            # Start the scheduler thread if not already running and we have scheduled orders
            if not DispatchOrdersToAGVsView._scheduler_running and scheduled_orders:
                if DispatchOrdersToAGVsView._scheduler_thread and DispatchOrdersToAGVsView._scheduler_thread.is_alive():
                    # Reuse existing thread
                    pass
                else:
                    # Create a new thread
                    DispatchOrdersToAGVsView._scheduler_thread = threading.Thread(
                        target=DispatchOrdersToAGVsView._run_scheduler,
                        daemon=True,
                        name="order_scheduler_thread"
                    )
                    DispatchOrdersToAGVsView._scheduler_thread.start()

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

        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response(
                {
                    "success": False,
                    "message": f"Error scheduling orders: {str(e)}",
                    "details": traceback_str
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _assign_single_order(self, order_id, algorithm="dijkstra"):
        """
        Assign a single order to an available AGV.
        
        Args:
            order_id: The ID of the order to assign
            algorithm: The pathfinding algorithm to use
            
        Returns:
            bool: True if assignment was successful, False otherwise
        """
        try:
            # Get the order
            order = Order.objects.get(order_id=order_id)
            
            # Check if order is still unassigned
            if hasattr(order, 'active_agv') and order.active_agv:
                print(f"Order {order_id} is already assigned to AGV {order.active_agv.agv_id}")
                return False

            # Find an available AGV for this order
            available_agv = Agv.objects.filter(
                motion_state=Agv.IDLE,
                preferred_parking_node=order.parking_node,
                active_order__isnull=True
            ).first()

            if not available_agv:
                print(f"No available AGV for order {order_id} at parking node {order.parking_node}")
                return False            # Use TaskDispatcher to process this single order
            dispatcher = TaskDispatcher()
            
            # Get the pathfinding algorithm
            from .pathfinding.factory import PathfindingFactory
            from .services.order_processor import OrderProcessor
            
            nodes, connections = dispatcher._validate_map_data()
            pathfinding_algorithm = PathfindingFactory.get_algorithm(algorithm, nodes, connections)
            if not pathfinding_algorithm:
                print(f"Invalid pathfinding algorithm: {algorithm}")
                return False

            order_processor = OrderProcessor(pathfinding_algorithm)
            
            # Validate order data
            if not order_processor.validate_order_data(order, nodes):
                print(f"Invalid order data for order {order_id}")
                return False

            # Process the order
            order_data = order_processor.process_order(order)
            if not order_data:
                print(f"Failed to process order {order_id}")
                return False

            # For now, set empty common nodes (would need to recalculate with other active orders)
            order_data["common_nodes"] = []
            order_data["adjacent_common_nodes"] = []

            # Update AGV with order data
            success = order_processor.update_agv_with_order(available_agv, order_data)
            if success:
                # Update AGV state to waiting
                available_agv.motion_state = Agv.WAITING
                available_agv.save()
                print(f"Successfully assigned order {order_id} to AGV {available_agv.agv_id}")
                return True
            else:
                print(f"Failed to update AGV {available_agv.agv_id} with order {order_id}")
                return False

        except Order.DoesNotExist:
            print(f"Order {order_id} not found")
            return False
        except Exception as e:
            print(f"Error assigning order {order_id}: {str(e)}")
            return False


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
