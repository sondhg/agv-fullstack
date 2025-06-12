import schedule
import time
import datetime
import threading
from typing import List, Dict, Tuple, Optional
from django.db.models import QuerySet

from ..models import Agv
from order_data.models import Order
from .algorithm1 import TaskDispatcher
from ..pathfinding.factory import PathfindingFactory
from .order_processor import OrderProcessor


class OrderSchedulerService:
    """
    Service class to handle order scheduling and assignment logic.
    """

    def __init__(self):
        self.scheduler_running = False
        self.scheduler_thread = None

    def get_unassigned_orders(self) -> QuerySet[Order]:
        """
        Get all unassigned orders.

        Returns:
            QuerySet[Order]: All orders without assigned AGVs
        """
        return Order.objects.filter(active_agv__isnull=True)

    def find_available_agv_for_order(self, order: Order) -> Optional[Agv]:
        """
        Find an available AGV for a specific order.

        Args:
            order: The order to find an AGV for

        Returns:
            Optional[Agv]: Available AGV or None if not found
        """
        return Agv.objects.filter(
            motion_state=Agv.IDLE,
            preferred_parking_node=order.parking_node,
            active_order__isnull=True
        ).first()

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

    def create_assignment_job(self, order_id: str, algorithm: str, assign_callback) -> callable:
        """
        Create a scheduled assignment job function.

        Args:
            order_id: The ID of the order to assign
            algorithm: The algorithm to use for assignment
            assign_callback: The callback function to assign the order

        Returns:
            callable: The assignment function to be scheduled
        """
        def create_assignment_function(order_id_val, algorithm_val):
            def assign_order():
                assign_callback(order_id_val, algorithm_val)
                return schedule.CancelJob  # Remove job after execution
            return assign_order

        return create_assignment_function(order_id, algorithm)

    def schedule_order_assignment(self, order: Order, algorithm: str, assign_callback) -> None:
        """
        Schedule an order for future assignment.

        Args:
            order: The order to schedule
            algorithm: The algorithm to use
            assign_callback: The callback function for assignment
        """
        assignment_function = self.create_assignment_job(
            order.order_id, algorithm, assign_callback)

        job = schedule.every().day.at(order.start_time.strftime("%H:%M:%S")).do(
            assignment_function
        )
        job.tag(f"order_{order.order_id}")

        print(
            f"Scheduled order {order.order_id} at {order.start_time.strftime('%H:%M:%S')}")

    def process_orders_for_scheduling(self, unassigned_orders: QuerySet[Order], algorithm: str, assign_callback) -> Tuple[List[Dict], List[Dict]]:
        """
        Process all unassigned orders for scheduling or immediate assignment.

        Args:
            unassigned_orders: QuerySet of unassigned orders
            algorithm: The algorithm to use for assignment
            assign_callback: The callback function for assignment

        Returns:
            Tuple[List[Dict], List[Dict]]: (scheduled_orders, immediate_orders)
        """
        scheduled_orders = []
        immediate_orders = []

        for order in unassigned_orders:
            available_agv = self.find_available_agv_for_order(order)

            if not available_agv:
                print(
                    f"No available AGV for order {order.order_id} at parking node {order.parking_node}")
                continue

            schedule_datetime = self.calculate_schedule_datetime(order)

            if self.is_order_scheduled_for_future(schedule_datetime):
                # Schedule for future assignment
                self.schedule_order_assignment(
                    order, algorithm, assign_callback)
                scheduled_order_info = self.create_scheduled_order_info(
                    order, available_agv, schedule_datetime)
                scheduled_orders.append(scheduled_order_info)
            else:
                # Assign immediately
                success = assign_callback(order.order_id, algorithm)
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
                    name="order_scheduler_thread"
                )
                self.scheduler_thread.start()

    def _run_scheduler(self) -> None:
        """Run the scheduler in a background thread"""
        self.scheduler_running = True
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        print("Order scheduler thread stopped")


class OrderAssignmentService:
    """
    Service class to handle individual order assignment logic.
    """

    def validate_order_assignment(self, order_id: str) -> Tuple[Optional[Order], Optional[Agv]]:
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
            available_agv = Agv.objects.filter(
                motion_state=Agv.IDLE,
                preferred_parking_node=order.parking_node,
                active_order__isnull=True
            ).first()

            if not available_agv:
                print(
                    f"No available AGV for order {order_id} at parking node {order.parking_node}")
                return None, None

            return order, available_agv

        except Order.DoesNotExist:
            print(f"Order {order_id} not found")
            return None, None

    def setup_pathfinding_components(self, algorithm: str) -> Tuple[Optional[object], Optional[OrderProcessor]]:
        """
        Set up pathfinding algorithm and order processor.

        Args:
            algorithm: The pathfinding algorithm to use

        Returns:
            Tuple[Optional[object], Optional[OrderProcessor]]: (pathfinding_algorithm, order_processor)
        """
        try:
            dispatcher = TaskDispatcher()
            nodes, connections = dispatcher._validate_map_data()

            pathfinding_algorithm = PathfindingFactory.get_algorithm(
                algorithm, nodes, connections)
            if not pathfinding_algorithm:
                print(f"Invalid pathfinding algorithm: {algorithm}")
                return None, None

            order_processor = OrderProcessor(pathfinding_algorithm)
            return pathfinding_algorithm, order_processor

        except Exception as e:
            print(f"Error setting up pathfinding components: {str(e)}")
            return None, None

    def process_and_assign_order(self, order: Order, agv: Agv, order_processor: OrderProcessor) -> bool:
        """
        Process order data and assign it to AGV.

        Args:
            order: The order to process
            agv: The AGV to assign the order to
            order_processor: The order processor instance

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get map data for validation
            dispatcher = TaskDispatcher()
            nodes, connections = dispatcher._validate_map_data()

            # Validate order data
            if not order_processor.validate_order_data(order, nodes):
                print(f"Invalid order data for order {order.order_id}")
                return False

            # Process the order
            order_data = order_processor.process_order(order)
            if not order_data:
                print(f"Failed to process order {order.order_id}")
                return False

            # Set common nodes (empty for now - would need recalculation with other active orders)
            order_data["common_nodes"] = []
            order_data["adjacent_common_nodes"] = []

            # Update AGV with order data
            success = order_processor.update_agv_with_order(agv, order_data)
            if success:
                # Update AGV state to waiting
                agv.motion_state = Agv.WAITING
                agv.save()
                return True
            else:
                print(
                    f"Failed to update AGV {agv.agv_id} with order {order.order_id}")
                return False

        except Exception as e:
            print(
                f"Error processing and assigning order {order.order_id}: {str(e)}")
            return False

    def assign_single_order(self, order_id: str, algorithm: str = "dijkstra") -> bool:
        """
        Assign a single order to an available AGV.

        Args:
            order_id: The ID of the order to assign
            algorithm: The pathfinding algorithm to use

        Returns:
            bool: True if assignment was successful, False otherwise
        """
        try:
            # Validate order and find AGV
            order, available_agv = self.validate_order_assignment(order_id)
            if not order or not available_agv:
                return False

            # Setup pathfinding components
            pathfinding_algorithm, order_processor = self.setup_pathfinding_components(
                algorithm)
            if not pathfinding_algorithm or not order_processor:
                return False

            # Process and assign the order
            success = self.process_and_assign_order(
                order, available_agv, order_processor)
            if success:
                # Send notification
                from ..views import send_order_assignment_notification
                message = f"Successfully assigned order {order_id} to AGV {available_agv.agv_id}"
                send_order_assignment_notification(
                    order_id, available_agv.agv_id, message)
                print(message)
                return True

            return False

        except Exception as e:
            print(f"Error assigning order {order_id}: {str(e)}")
            return False
