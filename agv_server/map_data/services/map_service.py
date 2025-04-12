"""Service layer for map data operations."""
import csv
import io
from typing import List, Dict, Any, Tuple, Optional
from django.db.models.query import QuerySet
from ..models import MapData, Connection, Direction
from ..constants import MapConstants, ErrorMessages


class MapService:
    @staticmethod
    def process_csv_data(data: str) -> List[List[str]]:
        """Process CSV data into a matrix."""
        reader = csv.reader(io.StringIO(data))
        return list(reader)

    @classmethod
    def import_connections(cls, data: str) -> Dict[str, Any]:
        """
        Import connection data from CSV.
        Returns a dictionary with status and message.
        """
        try:
            matrix = cls.process_csv_data(data)
            node_count = len(matrix)

            # Update or create map data entry
            map_data, _ = MapData.objects.get_or_create(id=1)
            map_data.node_count = node_count
            map_data.save()

            # Clear old connections
            Connection.objects.all().delete()

            # Save new connections
            connections_to_create = []
            for i in range(node_count):
                for j in range(node_count):
                    node1 = i + MapConstants.NODE_INDEX_OFFSET
                    node2 = j + MapConstants.NODE_INDEX_OFFSET

                    if node1 != node2 and int(matrix[i][j]) != MapConstants.NO_CONNECTION:
                        connections_to_create.append(
                            Connection(
                                node1=node1,
                                node2=node2,
                                distance=int(matrix[i][j])
                            )
                        )

            # Bulk create connections for better performance
            Connection.objects.bulk_create(connections_to_create)
            return {
                "success": True,
                "message": "Connection data imported successfully",
                "connection_count": len(connections_to_create)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error importing connections: {str(e)}"
            }

    @classmethod
    def import_directions(cls, data: str) -> Dict[str, Any]:
        """
        Import direction data from CSV.
        Returns a dictionary with status and message.
        """
        try:
            matrix = cls.process_csv_data(data)

            # Clear old directions
            Direction.objects.all().delete()

            # Save new directions
            directions_to_create = []
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    node1 = i + MapConstants.NODE_INDEX_OFFSET
                    node2 = j + MapConstants.NODE_INDEX_OFFSET

                    if int(matrix[i][j]) != MapConstants.NO_CONNECTION:
                        directions_to_create.append(
                            Direction(
                                node1=node1,
                                node2=node2,
                                direction=int(matrix[i][j])
                            )
                        )

            # Bulk create directions for better performance
            Direction.objects.bulk_create(directions_to_create)
            return {
                "success": True,
                "message": "Direction data imported successfully",
                "direction_count": len(directions_to_create)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error importing directions: {str(e)}"
            }

    @staticmethod
    def get_map_data() -> Dict[str, Any]:
        """Get all map data including nodes, connections, and directions."""
        nodes = list(Direction.objects.values_list(
            "node1", flat=True).distinct())
        connections = list(Connection.objects.values())
        directions = list(Direction.objects.values())

        # Check what data is available
        has_connections = len(connections) > 0
        has_directions = len(directions) > 0

        if not has_connections and not has_directions:
            return {
                "success": False,
                "message": "No map data available. Please import both connection and direction data.",
                "missing": ["connections", "directions"]
            }
        elif not has_connections:
            return {
                "success": False,
                "message": "Connection data is missing. Please import the connections CSV file.",
                "missing": ["connections"],
                "available": {
                    "nodes": nodes,
                    "directions": directions
                }
            }
        elif not has_directions:
            return {
                "success": False,
                "message": "Direction data is missing. Please import the directions CSV file.",
                "missing": ["directions"],
                "available": {
                    "nodes": list(Connection.objects.values_list("node1", flat=True).distinct()),
                    "connections": connections
                }
            }

        return {
            "success": True,
            "message": "Complete map data available",
            "data": {
                "nodes": nodes,
                "connections": connections,
                "directions": directions
            }
        }

    @staticmethod
    def delete_all_data() -> Dict[str, Any]:
        """Delete all map data."""
        try:
            connections_count = Connection.objects.count()
            directions_count = Direction.objects.count()

            Connection.objects.all().delete()
            Direction.objects.all().delete()
            MapData.objects.all().delete()

            return {
                "success": True,
                "message": "All map data deleted successfully",
                "deleted": {
                    "connections": connections_count,
                    "directions": directions_count
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting map data: {str(e)}"
            }
