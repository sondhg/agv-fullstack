"""
Implementation of Algorithm 1: Task Dispatching of the Central Controller
"""
from typing import List, Dict, Any, Optional
from order_data.models import Order
from map_data.models import Direction, Connection
from ...models import Schedule
from ...constants import ErrorMessages, AGVState
from ...pathfinding.factory import PathfindingFactory
from .shared_points import SharedPointsCalculator
from .schedule_generator import ScheduleGenerator
from agv_data.models import Agv, AGV_STATE_IDLE


class TaskDispatcher:
    def __init__(self):
        """Initialize TaskDispatcher with required data"""
        self.nodes, self.connections = self._validate_map_data()
        self.shared_points_calculator = SharedPointsCalculator(
            self.connections)
        self.schedule_generator = None  # Initialized in dispatch_tasks with algorithm

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
                motion_state=AGV_STATE_IDLE,
                preferred_parking_node=parking_node,
                active_schedule__isnull=True  # Extra check to ensure AGV is truly idle
            ).first()
            return agv
        except Exception as e:
            print(f"Error finding idle AGV: {str(e)}")
            return None

    def dispatch_tasks(self, algorithm: str = "dijkstra") -> List[Dict]:
        """
        Main implementation of Algorithm 1: Task Dispatching of the Central Controller.
        Dispatches tasks to idle AGVs and generates their schedules.

        Args:
            algorithm (str): The pathfinding algorithm to use. Defaults to "dijkstra".

        Returns:
            List[Dict]: Generated schedules for each task.

        Raises:
            ValueError: If there are no orders or if the pathfinding algorithm is invalid.
        """
        # Read input data and create task list T (line 2)
        tasks = list(Order.objects.all())
        if not tasks:
            raise ValueError(ErrorMessages.NO_ORDERS)

        # Initialize pathfinding algorithm and schedule generator
        pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, self.nodes, self.connections)
        if not pathfinding_algorithm:
            raise ValueError(ErrorMessages.INVALID_ALGORITHM)

        self.schedule_generator = ScheduleGenerator(pathfinding_algorithm)

        # First, generate all schedule data in memory
        schedule_data_list = []

        # For each task in the task list T (line 3)
        for task in tasks:
            # Skip if schedule already exists
            if Schedule.objects.filter(schedule_id=task.order_id).exists():
                continue

            # Validate task nodes exist in map
            if not self.schedule_generator.validate_task_data(task, self.nodes):
                continue

            try:
                # Find an idle AGV for this task (line 4)
                assigned_agv = self._find_idle_agv_for_task(task.parking_node)
                if not assigned_agv:
                    print(f"No idle AGV available for task {task.order_id} at parking node {task.parking_node}")
                    continue

                # Generate schedule data for task (without CP calculation yet)
                schedule_data = self.schedule_generator.generate_schedule_data(task)
                if schedule_data:
                    # Add AGV assignment to schedule data
                    schedule_data['assigned_agv'] = assigned_agv
                    schedule_data_list.append(schedule_data)

                    # Update AGV state to waiting (according to Algorithm 2 in paper)
                    assigned_agv.motion_state = AGVState.WAITING
                    assigned_agv.save()
            except Exception as e:
                print(f"Failed to process task {task.order_id}: {str(e)}")
                continue

        # Now calculate CP for each schedule using all schedules' residual paths
        for i, current_schedule in enumerate(schedule_data_list):
            # Get all other schedules' residual paths
            other_paths = []

            # Add residual paths from other schedules being created
            for j, other_schedule in enumerate(schedule_data_list):
                if i != j:  # Don't include current schedule
                    other_paths.append(other_schedule["residual_path"])

            # Calculate shared points and sequential shared points
            shared_points = self.shared_points_calculator.calculate_shared_points(
                current_schedule["residual_path"], other_paths
            )
            sequential_shared_points = self.shared_points_calculator.calculate_sequential_shared_points(
                shared_points)

            # Update the schedule data with calculated points
            current_schedule["cp"] = shared_points
            current_schedule["scp"] = sequential_shared_points

        # Finally, save all schedules to database
        saved_schedules = []
        for schedule_data in schedule_data_list:
            saved_schedule = self.schedule_generator.save_schedule(
                schedule_data)
            if saved_schedule:
                saved_schedules.append(saved_schedule)

        return saved_schedules
