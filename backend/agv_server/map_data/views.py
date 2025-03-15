import csv
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MapData, Connection, Direction


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
                if i != j and int(matrix[i][j]) != 100000:
                    Connection.objects.create(
                        node1=i, node2=j, distance=int(matrix[i][j]))

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
                if int(matrix[i][j]) != 5:  # Only save valid directions
                    Direction.objects.create(
                        node1=i, node2=j, direction=int(matrix[i][j]))

        return JsonResponse({"message": "Direction data imported successfully"}, status=200)


@csrf_exempt
def get_map_data(request):
    nodes = list(Direction.objects.values_list("node1", flat=True).distinct())
    connections = list(Connection.objects.values())
    directions = list(Direction.objects.values())

    return JsonResponse({
        "nodes": nodes,
        "connections": connections,
        "directions": directions
    }, status=200)
