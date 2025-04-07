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


class GenerateSchedulesView(APIView):
    def post(self, request):
        try:
            # Get the algorithm choice from the request body
            algorithm = request.data.get("algorithm", "dijkstra").lower()

            # Fetch all orders
            orders = Order.objects.all()
            if not orders.exists():
                return Response(
                    {"error": "No orders available to generate schedules."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch map data
            nodes = list(Direction.objects.values_list(
                "node1", flat=True).distinct())
            connections = list(Connection.objects.values()
                               )  # Includes distance
            if not nodes or not connections:
                return Response(
                    {"error": "Map data is incomplete or missing."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Initialize the selected pathfinding algorithm
            try:
                pathfinding_algorithm = PathfindingFactory.get_algorithm(
                    algorithm, nodes, connections
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            schedules = []
            all_paths = []  # To store paths for all orders for CP/SCP calculation

            for order in orders:
                # Skip existing schedules
                if Schedule.objects.filter(schedule_id=order.order_id).exists():
                    continue

                # Validate order data
                if not order.parking_node or not order.storage_node or not order.workstation_node:
                    print(f"Invalid order data for order {order.order_id}")
                    continue  # Skip invalid orders

                if order.parking_node not in nodes or order.storage_node not in nodes or order.workstation_node not in nodes:
                    print(f"Order {order.order_id} contains invalid nodes")
                    continue  # Skip orders with invalid nodes

                # Compute the shortest path based on the selected algorithm
                try:
                    path_to_storage = pathfinding_algorithm.find_shortest_path(
                        order.parking_node, order.storage_node
                    )
                    path_to_workstation = pathfinding_algorithm.find_shortest_path(
                        order.storage_node, order.workstation_node
                    )

                    # Combine all paths to form the complete route
                    path = (
                        path_to_storage
                        # Avoid duplicate storage_node
                        + path_to_workstation[1:]
                    )

                    if not path:
                        continue

                    # Add to all_paths for CP/SCP calculation
                    all_paths.append(path)

                    # Format the instruction set
                    shortest_path = path  # Keep formatting as JSON array
                except Exception as e:
                    return Response(
                        {"error": f"Failed to compute shortest path for order {order.order_id}: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Create a schedule
                schedule_data = {
                    "schedule_id": order.order_id,
                    "order_id": order.order_id,
                    "order_date": order.order_date,
                    "start_time": order.start_time,
                    "parking_node": order.parking_node,
                    "storage_node": order.storage_node,
                    "workstation_node": order.workstation_node,
                    "instruction_set": json.dumps(shortest_path),  # Store path
                    # Initialize traveling_info
                    "traveling_info": {"v_c": None, "v_n": None, "v_r": None},
                }
                serializer = ScheduleSerializer(data=schedule_data)
                if serializer.is_valid():
                    serializer.save()
                    schedules.append(serializer.data)
                else:
                    print(
                        f"Serialization failed for order {order.order_id}: {serializer.errors}")
                    return Response(
                        {"error": f"Failed to serialize schedule for order {order.order_id}: {serializer.errors}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Calculate CP and SCP for all schedules
            adjacency_matrix = pathfinding_algorithm.graph
            cp_scp_calculator = CpScpCalculator(adjacency_matrix)
            cp_scp_data = cp_scp_calculator.calculate_cp_and_scp(all_paths)

            # Update schedules with CP, SCP, and SP
            sp_calculator = SpCalculator(adjacency_matrix)
            for i, schedule in enumerate(Schedule.objects.all()):
                schedule.cp = cp_scp_data["cp"].get(i, [])
                schedule.scp = cp_scp_data["scp"].get(i, [])
                schedule.sp = sp_calculator.calculate_sp(
                    schedule.scp, residual_paths=all_paths
                )
                schedule.save()

            if not schedules:
                return Response(
                    {"error": "No schedules were generated. Check the input data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Schedules generated successfully.",
                    "schedules": schedules},
                status=status.HTTP_201_CREATED,
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
                {"message": f"Schedule {schedule_id} deleted successfully."},
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
                    {"error": "No schedule IDs provided for deletion."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count, _ = Schedule.objects.filter(
                schedule_id__in=schedule_ids).delete()
            return Response(
                {"message": f"{deleted_count} schedules deleted successfully."},
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

            # Update traveling information
            current_point = data.get("current_point")
            next_point = data.get("next_point")
            traveling_info = schedule.traveling_info or {
                "v_c": None, "v_n": None, "v_r": None}  # Ensure initialization

            if current_point is not None and next_point is not None:
                traveling_info["v_c"] = current_point
                traveling_info["v_n"] = next_point
                traveling_info["v_r"] = next_point
                schedule.traveling_info = traveling_info
                schedule.save()

            # Evaluate movement conditions
            scp = schedule.scp
            reserved_points = set(
                Schedule.objects.exclude(schedule_id=schedule_id)
                .values_list("traveling_info__v_r", flat=True)
            )
            reserved_by_no_spare = set(
                Schedule.objects.filter(spare_flag=False)
                .exclude(schedule_id=schedule_id)
                .values_list("traveling_info__v_r", flat=True)
            )
            spare_points = schedule.sp

            if MovementConditions.evaluate_condition_1(next_point, scp, reserved_points):
                schedule.state = 1  # Moving
                traveling_info["v_r"] = next_point
            elif MovementConditions.evaluate_condition_2(next_point, scp, reserved_points, reserved_by_no_spare):
                schedule.state = 1  # Moving
                traveling_info["v_r"] = next_point
            elif MovementConditions.evaluate_condition_3(next_point, scp, reserved_points, reserved_by_no_spare, spare_points):
                schedule.state = 1  # Moving
                traveling_info["v_r"] = next_point
            else:
                schedule.state = 2  # Waiting
                traveling_info["v_r"] = current_point

            schedule.traveling_info = traveling_info
            schedule.save()

            # Trigger deadlock detection
            heading_on_deadlocks = DeadlockDetector.detect_heading_on_deadlock()
            loop_deadlocks = DeadlockDetector.detect_loop_deadlock()

            if heading_on_deadlocks or loop_deadlocks:
                return Response(
                    {
                        "message": "Deadlock detected.",
                        "heading_on_deadlocks": heading_on_deadlocks,
                        "loop_deadlocks": loop_deadlocks,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                {
                    "message": f"Schedule {schedule_id} updated successfully.",
                    "traveling_info": traveling_info,
                    "state": schedule.state,
                },
                status=status.HTTP_200_OK,
            )
        except Schedule.DoesNotExist:
            return Response(
                {"error": f"Schedule {schedule_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while updating the schedule: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
