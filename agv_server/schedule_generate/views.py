from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from order_data.models import Order
from rest_framework.generics import ListAPIView
from map_data.models import Direction, Connection
import json
from .path_utils import format_instruction_set
from .pathfinding.factory import PathfindingFactory


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
            for order in orders:
                # Skip existing schedules
                if Schedule.objects.filter(schedule_id=order.order_id).exists():
                    continue

                # Validate order data
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
                    path_back_to_parking = pathfinding_algorithm.find_shortest_path(
                        order.workstation_node, order.parking_node
                    )

                    # Combine all paths to form the complete route
                    path = (
                        path_to_storage
                        # Avoid duplicate storage_node
                        + path_to_workstation[1:]
                        # Avoid duplicate workstation_node
                        + path_back_to_parking[1:]
                    )

                    if not path:
                        continue

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
