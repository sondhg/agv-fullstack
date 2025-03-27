from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from order_data.models import Order
from rest_framework.generics import ListAPIView
from .q_learning import QLearning
from .dijkstra import Dijkstra
from map_data.models import Direction, Connection  # Ensure distance data is used
import json
from .path_utils import format_instruction_set


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

            # Initialize pathfinding algorithms
            dijkstra = Dijkstra(nodes, connections)
            q_learning = QLearning(nodes, connections)

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
                    if algorithm == "q_learning":
                        q_learning.train(order.start_point, order.end_point)
                        path = q_learning.get_shortest_path(
                            order.start_point, order.end_point
                        )
                    elif algorithm == "dijkstra":
                        path = dijkstra.find_shortest_path(
                            order.start_point, order.end_point
                        )
                    else:
                        return Response(
                            {"error": f"Invalid algorithm: {algorithm}. Use 'q_learning' or 'dijkstra'."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if not path:
                        continue

                    # Format the instruction set
                    shortest_path = format_instruction_set(path)
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
