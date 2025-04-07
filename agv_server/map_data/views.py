import csv
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MapData, Connection, Direction
import logging
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

# Define a constant for no direct connection between nodes
NO_CONNECTION = 10000


@csrf_exempt
def import_connections(request):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        reader = csv.reader(io.StringIO(data))
        matrix = list(reader)

        node_count = len(matrix)

        # Update or create map data entry
        map_data, _ = MapData.objects.get_or_create(id=1)
        map_data.node_count = node_count
        map_data.save()

        # Clear old connections
        Connection.objects.all().delete()

        # Save new connections
        for i in range(node_count):
            for j in range(node_count):
                # Adjust indices to start from 1 instead of 0
                node1 = i + 1
                node2 = j + 1

                # Use the constant NO_CONNECTION instead of 10000
                if node1 != node2 and int(matrix[i][j]) != NO_CONNECTION:
                    Connection.objects.create(
                        node1=node1, node2=node2, distance=int(matrix[i][j])
                    )

        logger.info(f"Imported connections: {Connection.objects.all()}")
        return JsonResponse({"message": "Connection data imported successfully"}, status=200)


@csrf_exempt
def import_directions(request):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        reader = csv.reader(io.StringIO(data))
        matrix = list(reader)

        # Clear old directions
        Direction.objects.all().delete()

        # Save new directions
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                # Adjust indices to start from 1 instead of 0
                node1 = i + 1
                node2 = j + 1

                # Only save valid directions (value not equal to 10000)
                if int(matrix[i][j]) != NO_CONNECTION:
                    Direction.objects.create(
                        node1=node1, node2=node2, direction=int(matrix[i][j])
                    )

        logger.info(f"Imported directions: {Direction.objects.all()}")
        return JsonResponse({"message": "Direction data imported successfully"}, status=200)


@csrf_exempt
def get_map_data(request):
    try:
        nodes = list(Direction.objects.values_list(
            "node1", flat=True).distinct())
        connections = list(Connection.objects.values())
        directions = list(Direction.objects.values())

        if not nodes or not connections:
            return JsonResponse(
                {"message": "Map data is incomplete or missing."}, status=400
            )

        return JsonResponse(
            {"nodes": nodes, "connections": connections, "directions": directions},
            status=200,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_all_map_data(request):
    try:
        # Delete all map data
        Connection.objects.all().delete()
        Direction.objects.all().delete()
        MapData.objects.all().delete()

        logger.info("All map data deleted successfully.")
        return JsonResponse({"message": "All map data deleted successfully"}, status=200)
    except Exception as e:
        logger.error(f"Error deleting map data: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
