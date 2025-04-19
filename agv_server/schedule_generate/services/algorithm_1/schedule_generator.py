"""
Schedule generation module for the DSPA algorithm.
"""
from typing import Dict, List, Optional
from order_data.models import Order
from ...models import Schedule
from ...serializers import ScheduleSerializer
from ...constants import AGVState
from ...pathfinding.factory import PathfindingFactory


class ScheduleGenerator:
    def __init__(self, pathfinding_algorithm_instance):
        """
        Initialize the generator with a pathfinding algorithm.

        Args:
            pathfinding_algorithm_instance: Instance of a pathfinding algorithm
        """
        self.pathfinding_algorithm = pathfinding_algorithm_instance

    def _compute_path(self, task: Order) -> Optional[List[int]]:
        """
        Compute shortest path for a task using the pathfinding algorithm.

        Args:
            task (Order): The task to compute path for.

        Returns:
            Optional[List[int]]: Computed path from parking -> storage -> workstation.
            None if no valid path found.
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

    def generate_schedule_data(self, task: Order) -> Optional[Dict]:
        """
        Generate schedule data for a task without saving to database.

        Args:
            task (Order): The task to generate schedule data for.

        Returns:
            Optional[Dict]: Generated schedule data dictionary or None if path not found
        """
        # Find shortest route path P_i^j
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
            "state": AGVState.WAITING,  # Default state is WAITING per Algorithm 2
            "cp": [],  # Will be calculated later in dispatch_tasks
            "scp": [],  # Will be calculated later in dispatch_tasks
            "sp": {}  # Empty dict for spare points initially
        }

        return schedule_data

    def save_schedule(self, schedule_data: Dict) -> Optional[Dict]:
        """
        Save schedule data to database.

        Args:
            schedule_data (Dict): The schedule data to save.

        Returns:
            Optional[Dict]: Saved schedule data or None if validation fails.
        """
        # Get the assigned AGV from schedule data and remove it before serialization
        assigned_agv = schedule_data.pop('assigned_agv', None)

        serializer = ScheduleSerializer(data=schedule_data)
        if serializer.is_valid():
            schedule = serializer.save()
            
            if assigned_agv:
                # Set the AGV relationship after saving
                schedule.assigned_agv = assigned_agv
                schedule.save()
                
                # Update AGV's current schedule
                assigned_agv.active_schedule = schedule
                assigned_agv.save()

            return serializer.data
        else:
            print(
                f"Failed to serialize schedule for task {schedule_data['schedule_id']}: {serializer.errors}")
            return None

    def validate_task_data(self, task: Order, valid_nodes: List[int]) -> bool:
        """
        Validate task data against valid nodes.

        Args:
            task (Order): The task to validate
            valid_nodes (List[int]): List of valid node IDs in the map

        Returns:
            bool: True if task data is valid, False otherwise
        """
        # Check if all required nodes exist in the map
        return (task.parking_node in valid_nodes and
                task.storage_node in valid_nodes and
                task.workstation_node in valid_nodes)
