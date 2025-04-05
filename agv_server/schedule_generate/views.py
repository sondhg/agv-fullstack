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
                if order.start_point not in nodes or order.end_point not in nodes:
                    continue

                # Compute the shortest path based on the selected algorithm
                try:
                    path_to_end = pathfinding_algorithm.find_shortest_path(
                        order.start_point, order.end_point
                    )
                    path_back_to_start = pathfinding_algorithm.find_shortest_path(
                        order.end_point, order.start_point
                    )
                    path = path_to_end + path_back_to_start[1:]
                    if not path:
                        continue

                    # ! Instruction set with direction guide formatting
                    # shortest_path = format_instruction_set(path)
                    # ! Instruction set without direction guide formatting
                    shortest_path = path
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
                    "start_point": order.start_point,
                    "end_point": order.end_point,
                    "load_name": order.load_name,
                    "load_amount": order.load_amount,
                    "load_weight": order.load_weight,
                    "instruction_set": json.dumps(shortest_path),  # Store path
                }
                serializer = ScheduleSerializer(data=schedule_data)
                if serializer.is_valid():
                    serializer.save()
                    schedules.append(serializer.data)
                else:
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
