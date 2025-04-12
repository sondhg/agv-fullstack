from typing import List, Dict, Any
from django.db.models import QuerySet
from order_data.models import Order
from map_data.models import Direction, Connection
from ..models import Schedule
from ..serializers import ScheduleSerializer
from ..pathfinding.factory import PathfindingFactory
from ..pathfinding.cp_scp_calculator import CpScpCalculator
from ..pathfinding.sp_calculator import SpCalculator
import json


class ScheduleService:
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
        """Generate schedules for all orders"""
        # Validate map data
        nodes, connections = cls.validate_map_data()

        # Initialize pathfinding algorithm
        pathfinding_algorithm = PathfindingFactory.get_algorithm(
            algorithm, nodes, connections)

        schedules = []
        all_paths = []

        # Process each order
        for order in Order.objects.all():
            # Skip if schedule exists
            if Schedule.objects.filter(schedule_id=order.order_id).exists():
                continue

            # Validate order
            if not cls.validate_order_data(order, nodes):
                continue

            try:
                # Compute path
                path = cls.compute_path(pathfinding_algorithm, order)
                if not path:
                    continue

                all_paths.append(path)

                # Create schedule data
                schedule_data = {
                    "schedule_id": order.order_id,
                    "order_id": order.order_id,
                    "order_date": order.order_date,
                    "start_time": order.start_time,
                    "parking_node": order.parking_node,
                    "storage_node": order.storage_node,
                    "workstation_node": order.workstation_node,
                    "instruction_set": json.dumps(path),
                    "traveling_info": {"v_c": None, "v_n": None, "v_r": None},
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

        # Calculate CP and SCP for all schedules
        cls.update_schedule_points(pathfinding_algorithm, all_paths)

        return schedules

    @staticmethod
    def update_schedule_points(pathfinding_algorithm: Any, all_paths: List[List[int]]):
        """Update CP, SCP, and SP for all schedules"""
        adjacency_matrix = pathfinding_algorithm.graph
        cp_scp_calculator = CpScpCalculator(adjacency_matrix)
        cp_scp_data = cp_scp_calculator.calculate_cp_and_scp(all_paths)

        sp_calculator = SpCalculator(adjacency_matrix)
        for i, schedule in enumerate(Schedule.objects.all()):
            schedule.cp = cp_scp_data["cp"].get(i, [])
            schedule.scp = cp_scp_data["scp"].get(i, [])
            schedule.sp = sp_calculator.calculate_sp(
                schedule.scp, residual_paths=all_paths)
            schedule.save()

    @staticmethod
    def update_schedule_state(schedule: Schedule, current_point: int, next_point: int) -> Schedule:
        """Update schedule state and traveling info"""
        from ..pathfinding.movement_conditions import MovementConditions

        # Update traveling info
        traveling_info = schedule.traveling_info or {
            "v_c": None, "v_n": None, "v_r": None}
        traveling_info["v_c"] = current_point
        traveling_info["v_n"] = next_point
        traveling_info["v_r"] = next_point
        schedule.traveling_info = traveling_info

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

        # Evaluate conditions and update state
        if MovementConditions.evaluate_condition_1(next_point, schedule.scp, reserved_points):
            schedule.state = 1  # Moving
            traveling_info["v_r"] = next_point
        elif MovementConditions.evaluate_condition_2(next_point, schedule.scp, reserved_points, reserved_by_no_spare):
            schedule.state = 1  # Moving
            traveling_info["v_r"] = next_point
        elif MovementConditions.evaluate_condition_3(next_point, schedule.scp, reserved_points, reserved_by_no_spare, schedule.sp):
            schedule.state = 1  # Moving
            traveling_info["v_r"] = next_point
        else:
            schedule.state = 2  # Waiting
            traveling_info["v_r"] = current_point

        schedule.traveling_info = traveling_info
        schedule.save()
        return schedule
