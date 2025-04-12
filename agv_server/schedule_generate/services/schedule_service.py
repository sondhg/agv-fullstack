from typing import List, Dict, Any, Optional
from django.db.models import QuerySet
from order_data.models import Order
from map_data.models import Direction, Connection
from ..models import Schedule
from ..serializers import ScheduleSerializer
from ..pathfinding.factory import PathfindingFactory
from ..pathfinding.cp_scp_calculator import CpScpCalculator
from ..pathfinding.sp_calculator import SpCalculator
from ..pathfinding.movement_conditions import MovementConditions
from ..constants import AGVState
from map_data.services.map_service import MapService
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
            algorithm (str): The pathfinding algorithm to use.
            
        Returns:
            List[Dict]: The generated schedules.
        """
        # Validate map data
        nodes, connections = cls.validate_map_data()

        # Initialize pathfinding algorithm
        pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, nodes, connections)

        schedules = []
        all_paths = []

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
                    "v_n": path[1] if len(path) > 1 else None,  # Next position is the next point in path
                    "v_r": path[1] if len(path) > 1 else None   # Reserved position is same as next
                }

                # Create schedule data - Algorithm 1 lines 7-8
                schedule_data = {
                    "schedule_id": order.order_id,
                    "order_id": order.order_id,
                    "order_date": order.order_date,
                    "start_time": order.start_time,
                    "parking_node": order.parking_node,
                    "storage_node": order.storage_node,
                    "workstation_node": order.workstation_node,
                    "initial_path": json.dumps(path),
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

        # Calculate CP, SCP, and SP for all schedules - Algorithm 1 line 9
        if all_paths:
            cls.update_schedule_points(pathfinding_algorithm, all_paths)

        return schedules

    @staticmethod
    def update_schedule_points(pathfinding_algorithm: Any, all_paths: List[List[int]]):
        """
        Update CP, SCP, and SP for all schedules.
        Uses the CP/SCP calculator and SP calculator.
        
        Args:
            pathfinding_algorithm: The pathfinding algorithm with graph data.
            all_paths: List of paths for all AGVs.
        """
        adjacency_matrix = pathfinding_algorithm.graph
        
        # Calculate CP and SCP for all schedules - Definition 3 and 4
        cp_scp_calculator = CpScpCalculator(adjacency_matrix)
        cp_scp_data = cp_scp_calculator.calculate_cp_and_scp(all_paths)

        # Calculate SP for all schedules - Algorithm 4
        sp_calculator = SpCalculator(adjacency_matrix)
        
        for i, schedule in enumerate(Schedule.objects.all()):
            # Update CP and SCP
            schedule.cp = cp_scp_data["cp"].get(i, [])
            schedule.scp = cp_scp_data["scp"].get(i, [])
            
            # Calculate spare points
            schedule.sp = sp_calculator.calculate_sp(
                schedule.scp, residual_paths=all_paths)
                
            schedule.save()

    @staticmethod
    def update_schedule_state(schedule: Schedule, current_point: int, next_point: int) -> Schedule:
        """
        Update schedule state and traveling info according to the DSPA strategy.
        Implements Algorithm 2 from the paper.
        
        Args:
            schedule: The Schedule object to update
            current_point: Current position of the AGV
            next_point: Next intended position of the AGV
            
        Returns:
            The updated Schedule object
        """
        # Update traveling info
        traveling_info = schedule.traveling_info or {
            "v_c": None, "v_n": None, "v_r": None}
        traveling_info["v_c"] = current_point
        traveling_info["v_n"] = next_point
        
        # Get reserved points by other AGVs
        reserved_points = set(
            Schedule.objects.exclude(schedule_id=schedule.schedule_id)
            .values_list("traveling_info__v_r", flat=True)
        )
        
        # Get points reserved by AGVs without spare points (F^j = 0)
        reserved_by_no_spare = set(
            Schedule.objects.filter(spare_flag=False)
            .exclude(schedule_id=schedule.schedule_id)
            .values_list("traveling_info__v_r", flat=True)
        )

        # Ensure SCP is a list
        scp = schedule.scp
        if isinstance(scp, str):
            scp = json.loads(scp)

        # Handle spare point removal if needed (lines 14-16 in Algorithm 2)
        if MovementConditions.should_remove_current_spare_point(current_point, schedule.spare_flag, schedule.sp):
            current_point_str = str(current_point)
            if current_point_str in schedule.sp:
                sp_copy = dict(schedule.sp)
                sp_copy.pop(current_point_str, None)
                schedule.sp = sp_copy

        # Check movement conditions (lines 8-20 in Algorithm 2)
        apply_for_spare_points = False
        
        # Check Condition 1
        if MovementConditions.evaluate_condition_1(next_point, scp, reserved_points):
            # Condition 1 satisfied (lines 8-9 in Algorithm 2)
            schedule.state = AGVState.MOVING
            traveling_info["v_r"] = next_point
            
            # Update spare flag and clear SP if needed
            new_spare_flag, should_clear_sp = MovementConditions.should_update_spare_flag(
                current_point, next_point, scp, schedule.spare_flag, schedule.sp)
            schedule.spare_flag = new_spare_flag
            if should_clear_sp:
                schedule.sp = {}
                
        # Check Condition 2
        elif MovementConditions.evaluate_condition_2(next_point, scp, reserved_points, reserved_by_no_spare):
            # Condition 2 satisfied (lines 10-11 in Algorithm 2)
            schedule.state = AGVState.MOVING
            traveling_info["v_r"] = next_point
            
            # Update spare flag and clear SP if needed
            new_spare_flag, should_clear_sp = MovementConditions.should_update_spare_flag(
                current_point, next_point, scp, schedule.spare_flag, schedule.sp)
            schedule.spare_flag = new_spare_flag
            if should_clear_sp:
                schedule.sp = {}
                
        # Check Condition 3 or set up for spare point application
        else:
            if schedule.spare_flag:
                # Already has spare points, just check Condition 3
                if MovementConditions.evaluate_condition_3(next_point, scp, reserved_points, reserved_by_no_spare, schedule.sp):
                    schedule.state = AGVState.MOVING
                    traveling_info["v_r"] = next_point
                else:
                    # Can't move forward
                    schedule.state = AGVState.WAITING
                    traveling_info["v_r"] = current_point
            else:
                # Need to apply for spare points (will be handled by apply_for_spare_points method)
                schedule.state = AGVState.WAITING
                traveling_info["v_r"] = current_point
                apply_for_spare_points = True

        # Update traveling info
        schedule.traveling_info = traveling_info
        schedule.save()

        # Recalculate residual paths and update CP/SCP/SP if there's a significant change
        cls.update_all_residual_paths()
        
        # Refresh the schedule with the latest data
        return Schedule.objects.get(schedule_id=schedule.schedule_id)

    @classmethod
    def update_all_residual_paths(cls):
        """
        Update residual paths, CP, SCP, and SP for all schedules based on current positions.
        This ensures calculations are based on current positions, not original paths.
        """
        # Get map data
        map_data = MapService.get_map_data()
        if not map_data.get("success", False):
            return
            
        # Create adjacency matrix
        adjacency_matrix = {}
        connections = map_data["data"]["connections"]
        
        for conn in connections:
            node1 = conn["node1"]
            node2 = conn["node2"]
            
            if node1 not in adjacency_matrix:
                adjacency_matrix[node1] = {}
            if node2 not in adjacency_matrix:
                adjacency_matrix[node2] = {}
                
            adjacency_matrix[node1][node2] = conn["distance"]
            adjacency_matrix[node2][node1] = conn["distance"]  # Undirected graph
        
        # Calculate current residual paths for all AGVs
        residual_paths = []
        schedules = []
        
        for s in Schedule.objects.all():
            initial_path = s.initial_path
            if isinstance(initial_path, str):
                try:
                    initial_path = json.loads(initial_path)
                except json.JSONDecodeError:
                    initial_path = []
            
            # Get current point
            current_point = s.traveling_info.get("v_c")
            
            # Create residual path from current position
            if current_point is not None and isinstance(initial_path, list):
                try:
                    current_idx = initial_path.index(current_point)
                    residual_path = initial_path[current_idx:]
                    residual_paths.append(residual_path)
                    schedules.append(s)
                except ValueError:
                    # Current point not in initial path
                    residual_paths.append(initial_path)
                    schedules.append(s)
            else:
                residual_paths.append(initial_path)
                schedules.append(s)
        
        # Recalculate CP and SCP for all schedules
        cp_scp_calculator = CpScpCalculator(adjacency_matrix)
        cp_scp_data = cp_scp_calculator.calculate_cp_and_scp(residual_paths)
        
        # Update CP, SCP, and SP for all schedules
        sp_calculator = SpCalculator(adjacency_matrix)
        for i, s in enumerate(schedules):
            s.cp = cp_scp_data["cp"].get(i, [])
            s.scp = cp_scp_data["scp"].get(i, [])
            # Only update SP for AGVs that don't already have spare points
            if not s.spare_flag:
                s.sp = sp_calculator.calculate_sp(s.scp, residual_paths=residual_paths)
            s.save()

    @staticmethod
    def apply_for_spare_points(schedule: Schedule) -> bool:
        """
        Apply for spare points for a schedule.
        Implements the spare point application part of Algorithm 2 and Algorithm 4.
        
        Args:
            schedule: The Schedule object to apply spare points for
            
        Returns:
            bool: True if spare points were successfully allocated, False otherwise
        """
        # Get map data
        map_data = MapService.get_map_data()
        if not map_data.get("success", False):
            return False

        # Create adjacency matrix
        adjacency_matrix = {}
        connections = map_data["data"]["connections"]
        
        for conn in connections:
            node1 = conn["node1"]
            node2 = conn["node2"]
            
            if node1 not in adjacency_matrix:
                adjacency_matrix[node1] = {}
            if node2 not in adjacency_matrix:
                adjacency_matrix[node2] = {}
                
            adjacency_matrix[node1][node2] = conn["distance"]
            adjacency_matrix[node2][node1] = conn["distance"]  # Undirected graph

        # Get all residual paths
        residual_paths = []
        for s in Schedule.objects.all():
            initial_path = s.initial_path
            if isinstance(initial_path, str):
                try:
                    initial_path = json.loads(initial_path)
                except json.JSONDecodeError:
                    initial_path = []
            
            # Get current point
            current_point = s.traveling_info.get("v_c")
            
            # Create residual path from current position
            if current_point is not None and isinstance(initial_path, list):
                try:
                    current_idx = initial_path.index(current_point)
                    residual_path = initial_path[current_idx:]
                    residual_paths.append(residual_path)
                except ValueError:
                    # Current point not in initial path
                    residual_paths.append(initial_path)
            else:
                residual_paths.append(initial_path)

        # Calculate spare points using Algorithm 4
        sp_calculator = SpCalculator(adjacency_matrix)
        sp = sp_calculator.calculate_sp(schedule.scp, residual_paths)
        
        # Check if spare points were allocated successfully
        if sp:
            schedule.sp = sp
            schedule.spare_flag = True
            
            # Check if we can now move forward (Condition 3)
            traveling_info = schedule.traveling_info
            next_point = traveling_info["v_n"]
            
            # Get reserved points
            reserved_points = set(
                Schedule.objects.exclude(schedule_id=schedule.schedule_id)
                .values_list("traveling_info__v_r", flat=True)
            )
            reserved_by_no_spare = set(
                Schedule.objects.filter(spare_flag=False)
                .exclude(schedule_id=schedule.schedule_id)
                .values_list("traveling_info__v_r", flat=True)
            )
            
            # Check Condition 3
            scp = schedule.scp
            if isinstance(scp, str):
                scp = json.loads(scp)
                
            if MovementConditions.evaluate_condition_3(next_point, scp, reserved_points, reserved_by_no_spare, sp):
                schedule.state = AGVState.MOVING
                traveling_info["v_r"] = next_point
                schedule.traveling_info = traveling_info
            
            schedule.save()
            return True
        else:
            # Failed to allocate spare points
            schedule.spare_flag = False
            schedule.sp = {}
            schedule.save()
            return False
