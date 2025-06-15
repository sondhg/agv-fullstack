"""
Implementation of Algorithm 1: Task Dispatching of the Central Controller
Algorithm 1: Initial Path Planning and Shared Points Detection.
This algorithm handles task dispatching, initial path planning,
and shared points identification.
"""
import schedule
import time
import datetime
import threading
from typing import List, Dict, Optional, Tuple
from django.db.models import QuerySet
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
    Enhanced with scheduling capabilities and single order assignment.
    """

    def __init__(self):
        """Initialize TaskDispatcher with required data"""
        self.nodes, self.connections = self._validate_map_data()
        self.common_nodes_calculator = CommonNodesCalculator(
            self.connections)
        self.order_processor = None  # Initialized in dispatch_tasks with algorithm
        # Scheduling attributes
        self.scheduler_running = False
        self.scheduler_thread = None

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
        # Keep track of successfully assigned AGVs and their paths for updating common nodes
        processed_orders = []
        newly_assigned_agvs = []

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
                    "adjacent_common_nodes": order_data["adjacent_common_nodes"]})

                # Store successful assignments for later common nodes update
                newly_assigned_agvs.append({
                    "agv_id": assigned_agv.agv_id,
                    "remaining_path": order_data["remaining_path"]
                })                # Log the successful assignment
                print(
                    # After all new orders are assigned, recalculate common nodes for all active AGVs
                    f"Successfully assigned order {order_data['order_id']} to AGV {assigned_agv.agv_id}")
        # This ensures that all AGVs (both newly assigned and existing) have updated common_nodes
        # that reflect the current state with all active AGVs considered
        if processed_orders:
            try:
                from .common_nodes import recalculate_all_common_nodes
                recalculate_all_common_nodes(log_summary=True)
                print(
                    f"Recalculated common nodes for all AGVs after batch assignment of {len(processed_orders)} orders")
            except Exception as e:
                print(
                    f"Error recalculating common nodes after batch assignment: {str(e)}")

        return processed_orders

    def assign_single_order(self, order_id: str, algorithm: str = "dijkstra") -> bool:
        """
        Assign a single order to an available AGV.
        Enhanced version of single order assignment with proper error handling.

        Args:
            order_id: The ID of the order to assign
            algorithm: The pathfinding algorithm to use

        Returns:
            bool: True if assignment was successful, False otherwise
        """
        try:
            # Validate order and find AGV
            order, available_agv = self._validate_order_assignment(order_id)
            if not order or not available_agv:
                return False

            # Setup pathfinding algorithm if not already initialized
            if not self.order_processor or self.order_processor.pathfinding_algorithm.__class__.__name__.lower() != algorithm:
                pathfinding_algorithm = PathfindingFactory.get_algorithm(
                    algorithm, self.nodes, self.connections)
                if not pathfinding_algorithm:
                    print(f"Invalid pathfinding algorithm: {algorithm}")
                    return False
                # Process and assign the order
                self.order_processor = OrderProcessor(pathfinding_algorithm)
            success = self._process_and_assign_order(order, available_agv)
            if success:
                # Send notification with common nodes information
                try:
                    from ..views import send_order_assignment_notification
                    # Refresh AGV from database to get updated common_nodes
                    available_agv.refresh_from_db()
                    message = f"Successfully assigned order {order_id} to AGV {available_agv.agv_id}"
                    additional_data = {
                        "common_nodes_calculated": True,
                        "common_nodes_count": len(available_agv.common_nodes) if available_agv.common_nodes else 0,
                        "adjacent_common_nodes_count": len(available_agv.adjacent_common_nodes) if available_agv.adjacent_common_nodes else 0,
                        "remaining_path_length": len(available_agv.remaining_path) if available_agv.remaining_path else 0
                    }
                    send_order_assignment_notification(
                        order_id, available_agv.agv_id, message, additional_data)
                except ImportError:
                    # Handle case where notification function is not available
                    pass
                print(
                    f"Successfully assigned order {order_id} to AGV {available_agv.agv_id}")
                return True

            return False

        except Exception as e:
            print(f"Error assigning order {order_id}: {str(e)}")
            return False

    def _validate_order_assignment(self, order_id: str) -> Tuple[Optional[Order], Optional[Agv]]:
        """
        Validate if an order can be assigned and find available AGV.

        Args:
            order_id: The ID of the order to validate

        Returns:
            Tuple[Optional[Order], Optional[Agv]]: (order, available_agv) or (None, None) if invalid
        """
        try:
            order = Order.objects.get(order_id=order_id)

            # Check if order is still unassigned
            if hasattr(order, 'active_agv') and order.active_agv:
                print(
                    f"Order {order_id} is already assigned to AGV {order.active_agv.agv_id}")
                return None, None

            # Find an available AGV for this order
            available_agv = self._find_idle_agv_for_task(order.parking_node)
            if not available_agv:
                print(
                    f"No available AGV for order {order_id} at parking node {order.parking_node}")
                return None, None

            return order, available_agv

        except Order.DoesNotExist:
            print(f"Order {order_id} not found")
            return None, None

    def _process_and_assign_order(self, order: Order, agv: Agv) -> bool:
        """
        Process order data and assign it to AGV.

        Args:
            order: The order to process
            agv: The AGV to assign the order to

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate order data
            if not self.order_processor.validate_order_data(order, self.nodes):
                print(f"Invalid order data for order {order.order_id}")
                return False

            # Process the order
            order_data = self.order_processor.process_order(order)
            if not order_data:
                print(f"Failed to process order {order.order_id}")
                return False

            # Update AGV with order data
            success = self.order_processor.update_agv_with_order(
                agv, order_data)
            if not success:
                print(
                    f"Failed to update AGV {agv.agv_id} with order {order.order_id}")
                return False

            # Update AGV state to waiting
            agv.motion_state = Agv.WAITING
            # Recalculate common nodes for all AGVs (including the newly assigned AGV)
            agv.save()
            active_agvs_count = Agv.objects.filter(
                active_order__isnull=False).count()

            if active_agvs_count > 1:
                print(
                    f"Recalculating common nodes for all AGVs after assigning order {order.order_id} to AGV {agv.agv_id}")
                from .common_nodes import recalculate_all_common_nodes
                recalculate_all_common_nodes(log_summary=True)
            else:
                # If this is the only active AGV, ensure its common_nodes are empty
                agv.common_nodes = []
                agv.adjacent_common_nodes = []
                agv.save()
                print(
                    f"No other active AGVs, cleared common nodes for AGV {agv.agv_id}")

            return True

        except Exception as e:
            print(
                f"Error processing and assigning order {order.order_id}: {str(e)}")
            return False

    # Scheduling-related methods
    def get_unassigned_orders(self) -> QuerySet[Order]:
        """
        Get all unassigned orders.

        Returns:
            QuerySet[Order]: All orders without assigned AGVs
        """
        return Order.objects.filter(active_agv__isnull=True)

    def calculate_schedule_datetime(self, order: Order) -> datetime.datetime:
        """
        Calculate the scheduled datetime for an order.

        Args:
            order: The order to calculate schedule time for

        Returns:
            datetime.datetime: The scheduled datetime
        """
        return datetime.datetime.combine(order.order_date, order.start_time)

    def is_order_scheduled_for_future(self, schedule_datetime: datetime.datetime) -> bool:
        """
        Check if the order is scheduled for future execution.

        Args:
            schedule_datetime: The scheduled datetime

        Returns:
            bool: True if scheduled for future, False otherwise
        """
        return schedule_datetime > datetime.datetime.now()

    def create_scheduled_order_info(self, order: Order, agv: Agv, schedule_datetime: datetime.datetime) -> Dict:
        """
        Create information dictionary for a scheduled order.

        Args:
            order: The order being scheduled
            agv: The AGV assigned to the order
            schedule_datetime: When the order is scheduled

        Returns:
            Dict: Order scheduling information
        """
        now = datetime.datetime.now()
        return {
            "order_id": order.order_id,
            "agv_id": agv.agv_id,
            "parking_node": order.parking_node,
            "scheduled_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "seconds_from_now": (schedule_datetime - now).total_seconds()
        }

    def create_immediate_order_info(self, order: Order, agv: Agv) -> Dict:
        """
        Create information dictionary for an immediately assigned order.

        Args:
            order: The order being assigned
            agv: The AGV assigned to the order

        Returns:
            Dict: Order assignment information
        """
        return {
            "order_id": order.order_id,
            "agv_id": agv.agv_id,
            "parking_node": order.parking_node,
            "status": "assigned_immediately"
        }

    def schedule_order_assignment(self, order: Order, algorithm: str) -> None:
        """
        Schedule an order for future assignment.

        Args:
            order: The order to schedule
            algorithm: The algorithm to use
        """
        def create_assignment_function(order_id_val, algorithm_val):
            def assign_order():
                self.assign_single_order(order_id_val, algorithm_val)
                return schedule.CancelJob  # Remove job after execution
            return assign_order

        assignment_function = create_assignment_function(
            order.order_id, algorithm)

        job = schedule.every().day.at(order.start_time.strftime("%H:%M:%S")).do(
            assignment_function
        )
        job.tag(f"order_{order.order_id}")

        print(
            f"Scheduled order {order.order_id} at {order.start_time.strftime('%H:%M:%S')}")

    def process_orders_for_scheduling(self, algorithm: str = "dijkstra") -> Tuple[List[Dict], List[Dict]]:
        """
        Process all unassigned orders for scheduling or immediate assignment.

        Args:
            algorithm: The algorithm to use for assignment

        Returns:
            Tuple[List[Dict], List[Dict]]: (scheduled_orders, immediate_orders)
        """
        unassigned_orders = self.get_unassigned_orders()
        scheduled_orders = []
        immediate_orders = []

        for order in unassigned_orders:
            available_agv = self._find_idle_agv_for_task(order.parking_node)

            if not available_agv:
                print(
                    f"No available AGV for order {order.order_id} at parking node {order.parking_node}")
                continue

            schedule_datetime = self.calculate_schedule_datetime(order)

            if self.is_order_scheduled_for_future(schedule_datetime):
                # Schedule for future assignment
                self.schedule_order_assignment(order, algorithm)
                scheduled_order_info = self.create_scheduled_order_info(
                    order, available_agv, schedule_datetime)
                scheduled_orders.append(scheduled_order_info)
            else:
                # Assign immediately
                success = self.assign_single_order(order.order_id, algorithm)
                if success:
                    immediate_order_info = self.create_immediate_order_info(
                        order, available_agv)
                    immediate_orders.append(immediate_order_info)
                    print(
                        f"Assigned order {order.order_id} to AGV {available_agv.agv_id} immediately (scheduled time already passed)")

        return scheduled_orders, immediate_orders

    def start_scheduler_if_needed(self, scheduled_orders: List[Dict]) -> None:
        """
        Start the scheduler thread if there are scheduled orders and it's not already running.

        Args:
            scheduled_orders: List of scheduled orders
        """
        if not self.scheduler_running and scheduled_orders:
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                # Reuse existing thread
                pass
            else:
                # Create a new thread
                self.scheduler_thread = threading.Thread(
                    target=self._run_scheduler,
                    daemon=True,
                    name="task_dispatcher_scheduler_thread"
                )
                self.scheduler_thread.start()

    def _run_scheduler(self) -> None:
        """Run the scheduler in a background thread"""
        self.scheduler_running = True
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        print("Task dispatcher scheduler thread stopped")
