"""Service layer for map data operations."""

import csv
import io
from typing import List, Dict, Any, TypedDict, Optional
from ..models import MapData, Connection, Direction
from ..constants import MapConstants


class MapResponse(TypedDict):
    """Type definition for map operation responses."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]]


class MapService:
    """Service class for handling map-related operations."""

    @staticmethod
    def _create_success_response(message: str, **kwargs) -> MapResponse:
        """Create a standardized success response."""
        response = {"success": True, "message": message, "data": None}
        response.update(kwargs)
        return response

    @staticmethod
    def _create_error_response(message: str, **kwargs) -> MapResponse:
        """Create a standardized error response."""
        response = {"success": False, "message": message, "data": None}
        response.update(kwargs)
        return response

    @staticmethod
    def _process_matrix_nodes(matrix: List[List[str]], process_func) -> List[Any]:
        """Process matrix nodes with the given function."""
        items_to_create = []
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                node1 = i + MapConstants.NODE_INDEX_OFFSET
                node2 = j + MapConstants.NODE_INDEX_OFFSET
                value = int(matrix[i][j])

                if node1 != node2 and value != MapConstants.NO_CONNECTION:
                    items_to_create.append(process_func(node1, node2, value))
        return items_to_create

    @staticmethod
    def process_csv_data(data: str) -> List[List[str]]:
        """Process CSV data into a matrix."""
        try:
            return list(csv.reader(io.StringIO(data)))
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

    @classmethod
    def import_connections(cls, data: str) -> MapResponse:
        """Import connection data from CSV."""
        try:
            matrix = cls.process_csv_data(data)
            node_count = len(matrix)

            # Update or create map data entry
            map_data, _ = MapData.objects.get_or_create(id=1)
            map_data.node_count = node_count
            map_data.save()

            # Clear old connections
            Connection.objects.all().delete()

            # Process and create new connections
            connections = cls._process_matrix_nodes(
                matrix,
                lambda node1, node2, value: Connection(
                    node1=node1, node2=node2, distance=value
                ),
            )

            Connection.objects.bulk_create(connections)
            return cls._create_success_response(
                "Connection data imported successfully",
                connection_count=len(connections),
            )

        except Exception as e:
            return cls._create_error_response(f"Error importing connections: {str(e)}")

    @classmethod
    def import_directions(cls, data: str) -> MapResponse:
        """Import direction data from CSV."""
        try:
            matrix = cls.process_csv_data(data)

            # Clear old directions
            Direction.objects.all().delete()

            # Process and create new directions
            directions = cls._process_matrix_nodes(
                matrix,
                lambda node1, node2, value: Direction(
                    node1=node1, node2=node2, direction=value
                ),
            )

            Direction.objects.bulk_create(directions)
            return cls._create_success_response(
                "Direction data imported successfully", direction_count=len(directions)
            )

        except Exception as e:
            return cls._create_error_response(f"Error importing directions: {str(e)}")

    @staticmethod
    def get_map_data() -> MapResponse:
        """Get all map data including nodes, connections, and directions."""
        try:
            nodes = list(Direction.objects.values_list("node1", flat=True).distinct())
            connections = list(Connection.objects.values())
            directions = list(Direction.objects.values())

            has_connections = bool(connections)
            has_directions = bool(directions)

            if not has_connections and not has_directions:
                return MapService._create_error_response(
                    "No map data available. Please import both connection and direction data.",
                    missing=["connections", "directions"],
                )

            if not has_connections:
                return MapService._create_error_response(
                    "Connection data is missing. Please import the connections CSV file.",
                    missing=["connections"],
                    available={"nodes": nodes, "directions": directions},
                )

            if not has_directions:
                return MapService._create_error_response(
                    "Direction data is missing. Please import the directions CSV file.",
                    missing=["directions"],
                    available={
                        "nodes": list(
                            Connection.objects.values_list(
                                "node1", flat=True
                            ).distinct()
                        ),
                        "connections": connections,
                    },
                )

            return MapService._create_success_response(
                "Complete map data available",
                data={
                    "nodes": nodes,
                    "connections": connections,
                    "directions": directions,
                },
            )

        except Exception as e:
            return MapService._create_error_response(
                f"Error retrieving map data: {str(e)}"
            )

    @staticmethod
    def delete_all_data() -> MapResponse:
        """Delete all map data."""
        try:
            connections_count = Connection.objects.count()
            directions_count = Direction.objects.count()

            Connection.objects.all().delete()
            Direction.objects.all().delete()
            MapData.objects.all().delete()

            return MapService._create_success_response(
                "All map data deleted successfully",
                deleted={
                    "connections": connections_count,
                    "directions": directions_count,
                },
            )
        except Exception as e:
            return MapService._create_error_response(
                f"Error deleting map data: {str(e)}"
            )
