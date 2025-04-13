from typing import List, Dict, Any
from order_data.models import Order
from map_data.models import Direction, Connection
from ..models import Schedule
from ..serializers import ScheduleSerializer
from ..pathfinding.factory import PathfindingFactory
from ..constants import AGVState
import json


class ScheduleService:
    """
    Service for handling AGV schedule operations.
    Implements algorithms from the algorithms-pseudocode.tex.
    """

    @staticmethod
    def validate_map_data() -> tuple[list, list]:
        """Validate and return map data"""
        nodes = list(Direction.objects.values_list(
            "node1", flat=True).distinct())
        connections = list(Connection.objects.values())
        if not nodes or not connections:
            raise ValueError("Map data is incomplete or missing.")
        return nodes, connections

    @staticmethod
    def validate_order_data(order: Order, nodes: list) -> bool:
        """Validate order data"""
        if not all([order.parking_node, order.storage_node, order.workstation_node]):
            print(f"Invalid order data for order {order.order_id}")
            return False

        if not all(node in nodes for node in [order.parking_node, order.storage_node, order.workstation_node]):
            print(f"Order {order.order_id} contains invalid nodes")
            return False

        return True

    @staticmethod
    def compute_path(pathfinding_algorithm: Any, order: Order) -> list:
        """Compute shortest path for an order"""
        path_to_storage = pathfinding_algorithm.find_shortest_path(
            order.parking_node, order.storage_node
        )
        path_to_workstation = pathfinding_algorithm.find_shortest_path(
            order.storage_node, order.workstation_node
        )

        # Combine paths, avoiding duplicate storage_node
        return path_to_storage + path_to_workstation[1:]

    @classmethod
    def generate_schedules(cls, algorithm: str = "dijkstra") -> List[Dict]:
        """
        Generate schedules for all orders.
        Implements Algorithm 1 from the paper.

        Args:
            algorithm: The pathfinding algorithm to use

        Returns:
            List[Dict]: List of generated schedules
        """
        schedules = []
        all_paths = []

        # Get map data and validate it
        nodes, connections = cls.validate_map_data()

        # Get pathfinding algorithm with proper initialization
        pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, nodes, connections)
        if not pathfinding_algorithm:
            raise ValueError(f"Invalid algorithm: {algorithm}")

        # Process each order (task) - Algorithm 1 lines 3-9
        for order in Order.objects.all():
            # Skip if schedule already exists
            if Schedule.objects.filter(schedule_id=order.order_id).exists():
                continue

            # Validate order
            if not cls.validate_order_data(order, nodes):
                continue

            try:
                # Compute path - Algorithm 1 line 6
                path = cls.compute_path(pathfinding_algorithm, order)
                if not path:
                    continue

                all_paths.append(path)

                # Ensure path is proper Python list
                path = json.loads(json.dumps(path))

                # Initialize traveling_info with proper values - Algorithm 1 line 7
                traveling_info = {
                    "v_c": order.parking_node,  # Current position starts at parking node
                    # Next position is the next point in path
                    "v_n": path[1] if len(path) > 1 else None,
                    # Reserved position is same as next
                    "v_r": path[1] if len(path) > 1 else None
                }

                # Create schedule data - Algorithm 1 lines 7-8
                # IMPORTANT: initial_path (P_i) should NEVER be modified after creation
                # Only residual_path (Π_i) should be updated during execution
                schedule_data = {
                    "schedule_id": order.order_id,
                    "order_id": order.order_id,
                    "order_date": order.order_date,
                    "start_time": order.start_time,
                    "parking_node": order.parking_node,
                    "storage_node": order.storage_node,
                    "workstation_node": order.workstation_node,
                    "initial_path": json.dumps(path),  # P_i - never changes
                    # Π_i - updated during execution
                    "residual_path": json.dumps(path),
                    "traveling_info": traveling_info,
                    "state": AGVState.MOVING,  # Initialize AGV state to MOVING
                }

                serializer = ScheduleSerializer(data=schedule_data)
                if serializer.is_valid():
                    serializer.save()
                    schedules.append(serializer.data)
                else:
                    print(
                        f"Serialization failed for order {order.order_id}: {serializer.errors}")
                    raise ValueError(
                        f"Failed to serialize schedule for order {order.order_id}")

            except Exception as e:
                raise Exception(
                    f"Failed to process order {order.order_id}: {str(e)}")

        return schedules
