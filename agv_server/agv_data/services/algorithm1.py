"""
Implementation of Algorithm 1: Task Dispatching of the Central Controller
Algorithm 1: Initial Path Planning and Shared Points Detection.
This algorithm handles task dispatching, initial path planning,
and shared points identification.
"""
from typing import List, Dict, Optional
from order_data.models import Order
from map_data.models import Direction, Connection
from ..models import Agv
from ..constants import ErrorMessages
from ..pathfinding.factory import PathfindingFactory
from .common_nodes import CommonNodesCalculator
from .order_processor import OrderProcessor


class TaskDispatcher:
    """
    Handles assigning tasks (orders) to AGVs and computing their paths.
    Implementation of Algorithm 1 from the DSPA algorithm.
    """

    def __init__(self):
        """Initialize TaskDispatcher with required data"""
        self.nodes, self.connections = self._validate_map_data()
        self.common_nodes_calculator = CommonNodesCalculator(
            self.connections)
        self.order_processor = None  # Initialized in dispatch_tasks with algorithm

    def _validate_map_data(self) -> tuple[list, list]:
        """
        Validate and return map data.

        Returns:
            tuple[list, list]: A tuple containing nodes and connections.

        Raises:
            ValueError: If map data is incomplete or missing.
        """
        nodes = list(Direction.objects.values_list(
            "node1", flat=True).distinct())
        # Convert connections to use integers instead of strings for node values
        connections = []
        for conn in Connection.objects.values():
            connections.append({
                'node1': int(conn['node1']),
                'node2': int(conn['node2']),
                'distance': conn['distance']
            })
        if not nodes or not connections:
            raise ValueError(ErrorMessages.INVALID_MAP_DATA)
        return nodes, connections

    def _find_idle_agv_for_task(self, parking_node: int) -> Optional[Agv]:
        """
        Find an idle AGV that can handle a task with the given parking node.
        According to Algorithm 1 line 4, we need to find an AGV that:
        1. Is idle (SA^i = 0)
        2. Has preferred_parking_node matching the task's parking_node

        Args:
            parking_node (int): The parking node required for the task

        Returns:
            Optional[Agv]: An idle AGV that can handle the task, or None if no suitable AGV found
        """
        try:
            # Find an idle AGV with matching preferred parking node
            agv = Agv.objects.filter(
                motion_state=Agv.IDLE,
                preferred_parking_node=parking_node,
                active_order__isnull=True  # Ensure AGV is truly idle
            ).first()
            return agv
        except Exception as e:
            print(f"Error finding idle AGV: {str(e)}")
            return None

    def dispatch_tasks(self, algorithm: str = "dijkstra") -> List[Dict]:
        """
        Main implementation of Algorithm 1: Task Dispatching of the Central Controller.
        Dispatches tasks to idle AGVs and updates their paths and related data.

        Args:
            algorithm (str): The pathfinding algorithm to use. Defaults to "dijkstra".

        Returns:
            List[Dict]: Information about processed orders and assigned AGVs.

        Raises:
            ValueError: If there are no orders or if the pathfinding algorithm is invalid.
        """
        # Read input data and create task list T (line 2)
        tasks = list(Order.objects.filter(active_agv__isnull=True))
        if not tasks:
            raise ValueError(ErrorMessages.NO_ORDERS)

        # Initialize pathfinding algorithm and order processor
        pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, self.nodes, self.connections)
        if not pathfinding_algorithm:
            raise ValueError(ErrorMessages.INVALID_ALGORITHM)

        self.order_processor = OrderProcessor(pathfinding_algorithm)

        # First, generate all order processing data in memory
        orders_data_list = []

        # For each task in the task list T (line 3)
        for task in tasks:
            # Validate task nodes exist in map
            if not self.order_processor.validate_order_data(task, self.nodes):
                continue

            try:
                # Find an idle AGV for this task (line 4)
                assigned_agv = self._find_idle_agv_for_task(task.parking_node)
                if not assigned_agv:
                    print(
                        f"No idle AGV available for task {task.order_id} at parking node {task.parking_node}")
                    continue

                # Generate order data for task (without CP calculation yet)
                order_data = self.order_processor.process_order(task)
                if order_data:
                    # Add AGV assignment to order data
                    order_data['assigned_agv'] = assigned_agv
                    orders_data_list.append(order_data)

                    # Update AGV state to waiting (according to Algorithm 2 in paper)
                    assigned_agv.motion_state = Agv.WAITING
                    assigned_agv.save()
            except Exception as e:
                print(f"Failed to process task {task.order_id}: {str(e)}")
                continue

        # Now calculate common_nodes for each order using all orders' remaining paths
        for i, current_order in enumerate(orders_data_list):
            # Get all other orders' remaining paths
            other_paths = []

            # Add remaining paths from other orders being created
            for j, other_order in enumerate(orders_data_list):
                if i != j:  # Don't include current order
                    other_paths.append(other_order["remaining_path"])

            # Calculate shared points and sequential shared points
            common_nodes = self.common_nodes_calculator.calculate_common_nodes(
                current_order["remaining_path"], other_paths
            )
            sequential_common_nodes = self.common_nodes_calculator.calculate_sequential_common_nodes(
                common_nodes)

            # Update the order data with calculated points
            current_order["common_nodes"] = common_nodes
            current_order["adjacent_common_nodes"] = sequential_common_nodes

        # Finally, update all AGVs with their order data
        processed_orders = []
        for order_data in orders_data_list:
            assigned_agv = order_data.pop('assigned_agv')
            success = self.order_processor.update_agv_with_order(
                assigned_agv, order_data)
            if success:
                processed_orders.append({
                    "order_id": order_data["order_id"],
                    "agv_id": assigned_agv.agv_id,
                    "initial_path": order_data["initial_path"],
                    "common_nodes": order_data["common_nodes"],
                    "adjacent_common_nodes": order_data["adjacent_common_nodes"]
                })

        return processed_orders
