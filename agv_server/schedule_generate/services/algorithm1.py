from typing import List, Dict, Any
from order_data.models import Order
from map_data.models import Direction, Connection
from ..models import Schedule
from ..serializers import ScheduleSerializer
from ..pathfinding.factory import PathfindingFactory
from ..constants import AGVState, ErrorMessages


class TaskDispatcher:
    """
    Implementation of Algorithm 1 from the DSPA paper:
    Task Dispatching of the Central Controller
    """

    def __init__(self):
        """Initialize TaskDispatcher with required data"""
        self.nodes, self.connections = self._validate_map_data()
        self.pathfinding_algorithm = None

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

        # Initialize pathfinding algorithm
        self.pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, self.nodes, self.connections)
        if not self.pathfinding_algorithm:
            raise ValueError(ErrorMessages.INVALID_ALGORITHM)

        # First, generate all schedule data in memory
        schedule_data_list = []

        # For each task in the task list T (line 3)
        for task in tasks:
            # Skip if schedule already exists
            if Schedule.objects.filter(schedule_id=task.order_id).exists():
                continue

            # Validate task nodes exist in map
            if not self._validate_task_data(task):
                continue

            try:
                # Generate schedule data for task (without CP calculation yet)
                schedule_data = self._generate_schedule_data(task)
                if schedule_data:
                    schedule_data_list.append(schedule_data)
            except Exception as e:
                print(f"Failed to process task {task.order_id}: {str(e)}")
                continue

        # Now calculate CP for each schedule using all schedules' residual paths
        for i, current_schedule in enumerate(schedule_data_list):
            # Get all other schedules' residual paths
            other_paths = []
            # Add residual paths from existing schedules in database
            active_schedules = Schedule.objects.exclude(
                schedule_id=current_schedule["schedule_id"]
            ).filter(state__in=[1, 2])  # Moving or waiting states
            for schedule in active_schedules:
                other_paths.append(schedule.residual_path)

            # Add residual paths from other schedules being created
            for j, other_schedule in enumerate(schedule_data_list):
                if i != j:  # Don't include current schedule
                    other_paths.append(other_schedule["residual_path"])

            # Calculate shared points and sequential shared points
            shared_points = self._calculate_shared_points(
                current_schedule["residual_path"], other_paths
            )
            sequential_shared_points = self._calculate_sequential_shared_points(
                shared_points)

            # Update the schedule data with calculated points
            current_schedule["cp"] = shared_points
            current_schedule["scp"] = sequential_shared_points

        # Finally, save all schedules to database
        saved_schedules = []
        for schedule_data in schedule_data_list:
            serializer = ScheduleSerializer(data=schedule_data)
            if serializer.is_valid():
                serializer.save()
                saved_schedules.append(serializer.data)
            else:
                print(
                    f"Failed to serialize schedule for task {schedule_data['schedule_id']}: {serializer.errors}")

        return saved_schedules

    def _validate_task_data(self, task: Order) -> bool:
        """
        Validate task data has valid nodes that exist in the map.

        Args:
            task (Order): The task/order to validate.

        Returns:
            bool: True if task data is valid, False otherwise.
        """
        if not all([task.parking_node, task.storage_node, task.workstation_node]):
            print(f"Invalid task data for task {task.order_id}")
            return False

        if not all(node in self.nodes for node in [task.parking_node, task.storage_node, task.workstation_node]):
            print(f"Task {task.order_id} contains invalid nodes")
            return False

        return True

    def _generate_schedule_for_task(self, task: Order) -> Dict:
        """
        Generate a schedule for a single task, implementing lines 4-9 of Algorithm 1.

        Args:
            task (Order): The task to generate a schedule for.

        Returns:
            Dict: The generated schedule data.

        Raises:
            ValueError: If schedule serialization fails.
        """
        # Find shortest route path P_i^j (line 6)
        path = self._compute_path(task)
        if not path:
            return None

        # Get ALL other existing schedules' residual paths for calculating shared points
        other_residual_paths = []
        # Get all active schedules except this task's schedule
        active_schedules = Schedule.objects.exclude(schedule_id=task.order_id).filter(
            state__in=[1, 2])  # Moving or waiting states
        for schedule in active_schedules:
            # We need to use residual_path, not initial_path for CP calculation
            # This matches Definition 3 in the paper where CP uses current residual paths (Π)
            other_residual_paths.append(schedule.residual_path)

        # Calculate shared points (CP^i) and sequential shared points (SCP^i) (line 8)
        # According to Definition 3: CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}
        shared_points = self._calculate_shared_points(
            path, other_residual_paths)
        sequential_shared_points = self._calculate_sequential_shared_points(
            shared_points)

        # Create residual route Π_i and initialize traveling info (line 7)
        traveling_info = {
            "v_c": task.parking_node,  # Current position (at parking node)
            "v_n": path[1] if len(path) > 1 else None,  # Next position
            "v_r": path[1] if len(path) > 1 else None  # Reserved position
        }

        # Prepare schedule data with proper JSON handling
        # JSONField automatically handles serialization/deserialization
        schedule_data = {
            "schedule_id": task.order_id,
            "order_id": task.order_id,
            "order_date": task.order_date,
            "start_time": task.start_time,
            "parking_node": task.parking_node,
            "storage_node": task.storage_node,
            "workstation_node": task.workstation_node,
            "initial_path": path,  # No json.dumps() needed for JSONField
            "residual_path": path,  # No json.dumps() needed for JSONField
            "traveling_info": traveling_info,
            "state": AGVState.MOVING,
            "cp": shared_points,
            "scp": sequential_shared_points,
            "sp": {}  # Empty dict for spare points initially
        }

        # Save schedule (line 9)
        serializer = ScheduleSerializer(data=schedule_data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise ValueError(
                f"Failed to serialize schedule for task {task.order_id}: {serializer.errors}")

    def _generate_schedule_data(self, task: Order) -> Dict:
        """
        Generate schedule data for a task without saving to database.
        This method is similar to _generate_schedule_for_task but returns the data instead of saving.

        Args:
            task (Order): The task to generate schedule data for.

        Returns:
            Dict: The generated schedule data dictionary.
        """
        # Find shortest route path P_i^j (line 6)
        path = self._compute_path(task)
        if not path:
            return None

        # Create traveling info with initial positions
        traveling_info = {
            "v_c": task.parking_node,  # Current position (at parking node)
            "v_n": path[1] if len(path) > 1 else None,  # Next position
            "v_r": path[1] if len(path) > 1 else None  # Reserved position
        }

        # Prepare schedule data
        schedule_data = {
            "schedule_id": task.order_id,
            "order_id": task.order_id,
            "order_date": task.order_date,
            "start_time": task.start_time,
            "parking_node": task.parking_node,
            "storage_node": task.storage_node,
            "workstation_node": task.workstation_node,
            "initial_path": path,
            "residual_path": path,
            "traveling_info": traveling_info,
            "state": 1,  # Moving state
            "cp": [],  # Will be calculated later in dispatch_tasks
            "scp": [],  # Will be calculated later in dispatch_tasks
            "sp": {}  # Empty dict for spare points initially
        }

        return schedule_data

    def _compute_path(self, task: Order) -> list:
        """
        Compute shortest path for a task using selected pathfinding algorithm.

        Args:
            task (Order): The task to compute path for.

        Returns:
            list: Computed shortest path from parking -> storage -> workstation.
        """
        # Find path from parking to storage
        path_to_storage = self.pathfinding_algorithm.find_shortest_path(
            task.parking_node, task.storage_node
        )

        # Find path from storage to workstation
        path_to_workstation = self.pathfinding_algorithm.find_shortest_path(
            task.storage_node, task.workstation_node
        )

        # Combine paths, avoiding duplicate storage_node
        return path_to_storage + path_to_workstation[1:] if path_to_storage and path_to_workstation else None

    def _calculate_shared_points(self, current_path: list, other_paths: List[List]) -> list:
        """
        Calculate the shared points (CP^i) for a path based on Definition 3.
        For an active AGV r_i, CP^i consists of an ordered sequence of points shared with other AGVs:
        CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}

        Args:
            current_path (list): The path to calculate shared points for (Π_i)
            other_paths (List[List]): List of other residual paths to compare against (Π_j, j ≠ i)

        Returns:
            list: List of shared points in order of appearance in current_path
        """
        # Initialize shared points list to store the results
        shared_points = []

        # Create a set of all points in all other paths for faster lookups
        all_other_path_points = set()
        for path in other_paths:
            # Add all points from this path to our set
            all_other_path_points.update(path)

        # Check each point in current path
        for point in current_path:
            # If the point exists in any other path, add it to shared_points
            if point in all_other_path_points:
                shared_points.append(point)

        return shared_points  # Return points in the original order from current_path

    def _calculate_sequential_shared_points(self, shared_points: list) -> list:
        """
        Calculate sequential shared points (SCP^i) based on Definition 4 from the paper.
        Returns shared points that form sequences of connected points.

        Definition 4: For AGV r_i, its sequential shared points can be denoted as
        SCP^i = {v_p : D(v_p, v_q) ≠ 0, v_p ∈ CP^i, v_q ∈ CP^i}
        where v_q and v_p are the shared points of r_i, and D is the adjacency matrix.

        Args:
            shared_points (list): List of shared points to analyze

        Returns:
            list: List of sequential shared points in order of appearance
        """
        if not shared_points:
            return []

        # If there's only one shared point, it cannot form a sequence
        if len(shared_points) == 1:
            return []

        # Create a dictionary of adjacent points for faster lookup
        adjacent_points = {}
        for conn in self.connections:
            node1, node2 = conn['node1'], conn['node2']
            if node1 not in adjacent_points:
                adjacent_points[node1] = set()
            if node2 not in adjacent_points:
                adjacent_points[node2] = set()
            adjacent_points[node1].add(node2)
            adjacent_points[node2].add(node1)

        # Convert shared_points to set for faster lookup
        shared_points_set = set(shared_points)

        # Check each shared point to see if it has at least one adjacent shared point
        sequential_points = []
        for point in shared_points:
            # If the point doesn't exist in our adjacency map, skip it
            if point not in adjacent_points:
                continue

            # Check if any adjacent point is also a shared point
            has_adjacent_shared_point = any(adj_point in shared_points_set
                                            for adj_point in adjacent_points[point])

            if has_adjacent_shared_point:
                sequential_points.append(point)

        # Return sequential points in the original order from shared_points
        return [p for p in shared_points if p in sequential_points]
