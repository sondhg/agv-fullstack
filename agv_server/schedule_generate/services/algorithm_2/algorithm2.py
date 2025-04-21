"""
Implementation of Algorithm 2: Control Policy of the Central Controller

This module implements the central controller's logic for managing AGV movement
based on the DSPA algorithm described in algorithms-pseudocode.tex.

According to Definition 8 in the paper, an AGV's traveling information is denoted as:
I^i = {v_c^i, v_n^i, v_r^i}, where:
- v_c^i: Current position or the point the AGV last left
- v_n^i: Next point to be visited
- v_r^i: Point that the AGV has reserved

Key points from algorithms-pseudocode.tex:
1. AGVs can only move if next point is not reserved by another AGV
2. For sequential shared points (SCP), AGVs must have spare points to proceed
3. When AGV is in sequential shared points with spare points (F^i = 1), it should 
   remove the spare point for its current position when it reaches a new point
"""
from typing import Dict, List, Tuple
from agv_data.models import Agv
from schedule_generate.models import Schedule
from schedule_generate.constants import AGVState
from schedule_generate.services.algorithm_4.algorithm4 import allocate_spare_points


class ControlPolicyController:
    """
    Implements Algorithm 2: Control Policy of the Central Controller.

    This controller maintains the state of each AGV in the system, evaluates
    movement conditions, and updates their states. It also handles spare point
    allocation and management for conflict and deadlock resolution.
    """

    def __init__(self):
        """Initialize the Control Policy Controller."""
        pass

    def update_agv_state(self, agv_id: int) -> Dict:
        """
        Update the state of a specific AGV based on its current position and the
        positions of other AGVs in the system.

        This is the main implementation of Algorithm 2 from algorithms-pseudocode.tex.

        Args:
            agv_id (int): The ID of the AGV to update state for

        Returns:
            Dict: Updated state information for the AGV
        """
        try:
            # Get the AGV and its schedule
            agv = Agv.objects.get(agv_id=agv_id)

            # If AGV has no active schedule, it's idle
            if not agv.active_schedule:
                return {
                    "success": False,
                    "message": "AGV has no active schedule"
                }

            # Default state is waiting (as per Algorithm 2, line 4)
            agv.motion_state = AGVState.WAITING

            # Get schedule details
            schedule = agv.active_schedule

            # If the AGV has reached its workstation node (destination for tasks)
            if agv.current_node == schedule.workstation_node:
                # Completed task, set AGV to idle (as per the AGV's journey definition)
                # Parking node -> Storage node -> Workstation node (completion)
                agv.motion_state = AGVState.IDLE
                agv.active_schedule = None
                agv.spare_flag = False
                agv.spare_points = {}
                agv.next_node = None
                agv.reserved_node = None
                agv.save()

                # Update schedule status
                schedule.status = "completed"
                schedule.save()

                return {
                    "success": True,
                    "message": "Task completed",
                    "state": "idle"
                }

            # Update travel information (I^i), residual path (Π_i),
            # shared points (CP^i), and sequential shared points (SCP^i)
            # This corresponds to line 6 in Algorithm 2
            self._update_travel_information(agv, schedule)

            # Evaluate movement conditions and update state
            # This implements the core decision logic of Algorithm 2 (lines 7-20)
            can_move, should_apply_spare_points = self._evaluate_movement_conditions(
                agv, schedule)

            # If AGV needs to apply for spare points
            if should_apply_spare_points:
                # If spare_flag is already set, just remove current spare point (line 14-16)
                if agv.spare_flag:
                    self._remove_current_spare_point(agv)
                else:
                    # Apply for spare points (line 17)
                    self._apply_for_spare_points(agv, schedule)

                # Re-evaluate movement conditions after spare point application
                can_move, _ = self._evaluate_movement_conditions(agv, schedule)

            # Update AGV state based on evaluation result
            if can_move:
                # AGV can move (satisfied one of the movement conditions)
                agv.motion_state = AGVState.MOVING
                # Reserved node is set to the next node when AGV is allowed to move
                # This implements the reservation mechanism described in the paper
                agv.reserved_node = agv.next_node
                agv.save()
                return {
                    "success": True,
                    "message": "AGV can move to next point",
                    "state": "moving",
                    "next_node": agv.next_node
                }
            else:
                # AGV must wait (did not satisfy any movement condition)
                # When waiting, the AGV reserves its current position
                agv.reserved_node = agv.current_node
                agv.save()
                return {
                    "success": True,
                    "message": "AGV must wait at current point",
                    "state": "waiting"
                }

        except Agv.DoesNotExist:
            return {
                "success": False,
                "message": f"AGV with ID {agv_id} not found"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating AGV state: {str(e)}"
            }

    def _update_travel_information(self, agv: Agv, schedule: Schedule) -> None:
        """
        Update the travel information for an AGV based on its current position and schedule.
        This includes updating the next node in the residual path.

        This function implements part of line 6 in Algorithm 2, specifically updating
        the traveling information I^i and determining the next node (v_n^i).

        Args:
            agv (Agv): The AGV object
            schedule (Schedule): The AGV's active schedule
        """
        # Get current residual path from schedule
        residual_path = schedule.residual_path

        if not residual_path:
            # No residual path, AGV should be at destination (workstation_node)
            return

        # Update the residual path if the AGV has reached the first point in it
        if agv.current_node == residual_path[0]:
            # Remove the current node from the residual path as it's been visited
            # This implements Definition 2 from the algorithms-pseudocode.tex
            # "After an AGV reaches an identification point, the residual path of the AGV is updated."
            residual_path = residual_path[1:]
            schedule.residual_path = residual_path
            schedule.save()

        # Update next node (v_n^i) based on current position and residual path
        if not residual_path:
            # Residual path is now empty, no next node
            agv.next_node = None
        elif agv.current_node == residual_path[0]:
            # This could happen if we didn't remove the current node from residual path
            # Current node is the first in residual path, next node is the second
            if len(residual_path) > 1:
                agv.next_node = residual_path[1]
            else:
                # This was the last point, no next node
                agv.next_node = None
        else:
            # Current node is not in residual path (e.g., after deadlock resolution)
            # Next node is the first in residual path
            agv.next_node = residual_path[0]

    def _evaluate_movement_conditions(self, agv: Agv, schedule: Schedule) -> Tuple[bool, bool]:
        """
        Evaluate the three movement conditions from Algorithm 2 to determine if an AGV can move.

        This implements the core decision logic from lines 7-20 of Algorithm 2.

        The three conditions are:
        1. v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
        2. v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} and v_n^i ∉ {v_r^j, j ≠ i}
        3. v_n^i ∈ SCP^i and ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0} but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}

        Args:
            agv (Agv): The AGV object
            schedule (Schedule): The AGV's active schedule

        Returns:
            Tuple[bool, bool]: (can_move, should_apply_spare_points)
                - can_move: True if any condition is satisfied and AGV can move
                - should_apply_spare_points: True if AGV needs to apply for spare points
        """
        # If next_node is None, AGV cannot move
        if agv.next_node is None:
            return False, False

        # Check if next node is reserved by another AGV
        # This is a key part of all three conditions: v_n^i ∉ {v_r^j, j ≠ i}
        reserved_by_others = self._is_node_reserved_by_others(
            agv.next_node, agv.agv_id)

        if reserved_by_others:
            # Next point is reserved by another AGV, so AGV cannot move
            # None of the three conditions can be satisfied
            return False, False

        # Get sequential shared points from schedule
        scp = schedule.scp

        # Condition 1: v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
        # This means: next node is not in sequential shared points and not reserved by others
        condition_1 = agv.next_node not in scp and not reserved_by_others

        if condition_1:
            # Condition 1 is satisfied, AGV can move and clear spare points
            # This implements lines 9-10 in Algorithm 2
            agv.spare_flag = False
            agv.spare_points = {}
            return True, False

        # Check if there are any sequential shared points with reservations by AGVs without spare points
        # This is needed for Condition 2: ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0}
        scp_with_no_spare_reservations = self._check_scp_with_no_spare_reservations(
            scp, agv.agv_id)

        # Condition 2: v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} and v_n^i ∉ {v_r^j, j ≠ i}
        # This means: next node is in sequential shared points, no SCP points are reserved by AGVs without spare points
        condition_2 = (agv.next_node in scp and
                       not scp_with_no_spare_reservations and
                       not reserved_by_others)

        if condition_2:
            # Condition 2 is satisfied, AGV can move and clear spare points
            # This implements lines 11-12 in Algorithm 2
            agv.spare_flag = False
            agv.spare_points = {}
            return True, False

        # For Condition 3, we need to check if AGV has spare points or needs to apply for them
        # Condition 3 requires: SP^i ≠ ∅ (AGV has spare points)
        if agv.spare_flag:
            # AGV already has spare points (F^i = 1)
            # Need to remove current spare point as per lines 14-16 in Algorithm 2
            return True, True  # We'll need to remove current spare point
        else:
            # AGV needs to apply for spare points as per line 17 in Algorithm 2
            return False, True

    def _is_node_reserved_by_others(self, node: int, exclude_agv_id: int) -> bool:
        """
        Check if a node is reserved by any other AGV.

        This helps evaluate the condition v_n^i ∉ {v_r^j, j ≠ i} which appears
        in all three movement conditions.

        Args:
            node (int): The node to check
            exclude_agv_id (int): The AGV ID to exclude from the check

        Returns:
            bool: True if node is reserved by another AGV, False otherwise
        """
        return Agv.objects.filter(
            reserved_node=node
        ).exclude(
            agv_id=exclude_agv_id
        ).exists()

    def _check_scp_with_no_spare_reservations(self, scp: List[int], exclude_agv_id: int) -> bool:
        """
        Check if any point in the sequential shared points is reserved by an AGV 
        without spare points (F^j = 0).

        This helps evaluate the condition ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0}
        from Condition 3, and its negation for Condition 2.

        Args:
            scp (List[int]): List of sequential shared points
            exclude_agv_id (int): The AGV ID to exclude from the check

        Returns:
            bool: True if any SCP point is reserved by an AGV without spare points
        """
        for point in scp:
            # Check if point is reserved by an AGV without spare points
            if Agv.objects.filter(
                reserved_node=point,
                spare_flag=False
            ).exclude(
                agv_id=exclude_agv_id
            ).exists():
                return True
        return False

    def _apply_for_spare_points(self, agv: Agv, schedule: Schedule) -> None:
        """
        Apply for spare points for an AGV's sequential shared points.

        This implements line 17 in Algorithm 2, which calls Algorithm 4
        for spare point allocation.

        Args:
            agv (Agv): The AGV object
            schedule (Schedule): The AGV's active schedule
        """
        # Get sequential shared points from schedule
        scp = schedule.scp

        if not scp:
            # No sequential shared points, no need for spare points
            agv.spare_flag = False
            agv.spare_points = {}
            return

        # Get all residual paths of other AGVs
        all_residual_paths = []
        for other_agv in Agv.objects.exclude(agv_id=agv.agv_id):
            if other_agv.active_schedule:
                all_residual_paths.append(
                    other_agv.active_schedule.residual_path)

        # Call algorithm4's allocate_spare_points to allocate spare points
        spare_points = allocate_spare_points(scp, all_residual_paths)

        if spare_points:
            # Successfully allocated spare points, set F^i = 1
            agv.spare_flag = True
            agv.spare_points = spare_points
        else:
            # Failed to allocate spare points, set F^i = 0
            agv.spare_flag = False
            agv.spare_points = {}

    def _remove_current_spare_point(self, agv: Agv) -> None:
        """
        Remove the spare point allocated for the AGV's current position.
        According to Algorithm 2 lines 14-16, when F^i = 1, remove SP^i(v_c^i).

        Args:
            agv (Agv): The AGV object
        """
        if not agv.spare_flag or not agv.spare_points:
            return

        # Convert current_node to string since spare_points keys are stored as strings
        current_node_str = str(agv.current_node)

        # Remove the spare point for current position if it exists
        if current_node_str in agv.spare_points:
            spare_points = agv.spare_points.copy()
            spare_points.pop(current_node_str, None)
            agv.spare_points = spare_points

            # If no more spare points left, reset spare_flag
            if not agv.spare_points:
                agv.spare_flag = False
