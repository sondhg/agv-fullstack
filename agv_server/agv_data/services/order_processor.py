"""
Order processing module for the DSPA algorithm.
This replaces the schedule generator module from the schedule_generate app.
"""
from typing import Dict, List, Optional
from order_data.models import Order
from ..models import Agv


class OrderProcessor:
    """
    Processes orders to generate paths and update AGV information.
    """

    def __init__(self, pathfinding_algorithm_instance):
        """
        Initialize the processor with a pathfinding algorithm.

        Args:
            pathfinding_algorithm_instance: Instance of a pathfinding algorithm
        """
        self.pathfinding_algorithm = pathfinding_algorithm_instance

    def _compute_path(self, order: Order) -> Optional[List[int]]:
        """
        Compute shortest path for an order using the pathfinding algorithm.

        Args:
            order (Order): The order to compute path for.

        Returns:
            Optional[List[int]]: Computed path from parking → storage → workstation.
            None if no valid path found.
        """
        # Find path from parking to storage
        path_to_storage = self.pathfinding_algorithm.find_shortest_path(
            order.parking_node, order.storage_node
        )

        # Find path from storage to workstation
        path_to_workstation = self.pathfinding_algorithm.find_shortest_path(
            order.storage_node, order.workstation_node
        )

        # Combine paths, avoiding duplicate storage_node
        return path_to_storage + path_to_workstation[1:] if path_to_storage and path_to_workstation else None

    def process_order(self, order: Order) -> Optional[Dict]:
        """
        Process an order to generate path data without updating database.

        Args:
            order (Order): The order to process.

        Returns:
            Optional[Dict]: Generated order data dictionary or None if path not found
        """
        # Find shortest route path P_i^j
        path = self._compute_path(order)
        if not path:
            return None

        # Prepare order process data
        order_data = {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "start_time": order.start_time,
            "parking_node": order.parking_node,
            "storage_node": order.storage_node,
            "workstation_node": order.workstation_node,
            "initial_path": path,
            "remaining_path": path,
            "common_nodes": [],  # Will be calculated later in process_tasks
            "adjacent_common_nodes": []  # Will be calculated later in process_tasks
        }

        return order_data

    def update_agv_with_order(self, agv: Agv, order_data: Dict) -> bool:
        """
        Update AGV with order data.

        Args:
            agv (Agv): The AGV to update.
            order_data (Dict): The order data to update the AGV with.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            # Get the order instance
            order = Order.objects.get(order_id=order_data["order_id"])

            # Update AGV with order data
            agv.active_order = order
            agv.initial_path = order_data["initial_path"]
            agv.remaining_path = order_data["remaining_path"]
            agv.common_nodes = order_data["common_nodes"]
            agv.adjacent_common_nodes = order_data["adjacent_common_nodes"]
            agv.save()

            return True
        except Exception as e:
            print(
                f"Failed to update AGV {agv.agv_id} with order {order_data['order_id']}: {str(e)}")
            return False

    def validate_order_data(self, order: Order, valid_nodes: List[int]) -> bool:
        """
        Validate order data against valid nodes.

        Args:
            order (Order): The order to validate
            valid_nodes (List[int]): List of valid node IDs in the map

        Returns:
            bool: True if order data is valid, False otherwise
        """
        # Check if all required nodes exist in the map
        return (order.parking_node in valid_nodes and
                order.storage_node in valid_nodes and
                order.workstation_node in valid_nodes)
