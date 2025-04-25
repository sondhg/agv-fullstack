"""
Main controller for AGV control policy.

This module implements the central controller's logic for managing AGV movement
based on Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.

The controller handles the high-level decision-making and delegates specific tasks
to specialized modules.
"""
from typing import Dict, Optional

from order_data.models import Order
from ..models import Agv
from ..constants import AGVState
from .travel_information import update_travel_information
from .movement_conditions import evaluate_movement_conditions
from .spare_points_manager import remove_current_spare_point, check_and_update_agvs_at_spare_points, apply_for_spare_points
from .utils import is_node_reserved_by_others


class ControlPolicyController:
    """
    Implements Algorithm 2: Control Policy of the Central Controller.

    This controller maintains the state of each AGV in the system, evaluates
    movement conditions, and updates their states. It also handles spare point
    allocation and management for conflict and deadlock resolution.
    """

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
            agv = self._get_agv(agv_id)
            if not agv:
                return self._create_error_response(f"AGV with ID {agv_id} not found")

            if not agv.active_order:
                return self._create_error_response("AGV has no active order")

            # Default state is waiting (as per Algorithm 2, line 4)
            agv.motion_state = AGVState.WAITING

            # Check if task is completed
            if self._is_task_completed(agv):
                return self._complete_agv_task(agv, agv.active_order)

            # Update travel information (line 6 in Algorithm 2)
            update_travel_information(agv)

            # Handle movement decision
            result_info = self._handle_movement_decision(agv)

            # Update other AGVs if needed
            if agv.motion_state == AGVState.MOVING:
                updated_agvs = check_and_update_agvs_at_spare_points(agv_id)
                if updated_agvs:
                    result_info["updated_agvs"] = updated_agvs
                    result_info["message"] += f". Also updated AGVs {updated_agvs} to return from spare points."

            return result_info

        except Exception as e:
            return self._create_error_response(f"Error updating AGV state: {str(e)}")

    def _get_agv(self, agv_id: int) -> Optional[Agv]:
        """Get AGV by ID or return None."""
        try:
            return Agv.objects.get(agv_id=agv_id)
        except Agv.DoesNotExist:
            return None

    def _is_task_completed(self, agv: Agv) -> bool:
        """Check if AGV has reached its destination."""
        return agv.current_node == agv.active_order.workstation_node

    def _handle_movement_decision(self, agv: Agv) -> Dict:
        """Handle AGV movement decision based on current state and conditions."""
        # Check if AGV can return from spare point
        if self._can_return_from_spare_point(agv):
            return self._return_agv_from_spare_point(agv)

        return self._evaluate_and_update_agv_movement(agv)

    def _can_return_from_spare_point(self, agv: Agv) -> bool:
        """Check if AGV can return from spare point to main path."""
        return (agv.spare_flag and
                agv.next_node and
                not is_node_reserved_by_others(agv.next_node, agv.agv_id) and
                agv.residual_path and
                agv.next_node == agv.residual_path[0])

    def _complete_agv_task(self, agv: Agv, order: Order) -> Dict:
        """Complete the current task for an AGV."""
        self._reset_agv_state(agv)
        order.status = "completed"
        order.save()

        return {
            "success": True,
            "message": "Task completed",
            "state": "idle"
        }

    def _reset_agv_state(self, agv: Agv) -> None:
        """Reset AGV state to idle."""
        agv.motion_state = AGVState.IDLE
        agv.active_order = None
        agv.spare_flag = False
        agv.spare_points = {}
        agv.previous_node = None
        agv.current_node = None
        agv.next_node = None
        agv.reserved_node = None
        agv.save()

    def _return_agv_from_spare_point(self, agv: Agv) -> Dict:
        """Move an AGV from its spare point back to its original path."""
        agv.spare_flag = False
        agv.spare_points = {}
        agv.motion_state = AGVState.MOVING
        agv.reserved_node = agv.next_node
        agv.save()

        return {
            "success": True,
            "message": "AGV returning from spare point to original path",
            "state": "moving",
            "next_node": agv.next_node
        }

    def _evaluate_and_update_agv_movement(self, agv: Agv) -> Dict:
        """Evaluate movement conditions and update AGV state."""
        can_move, should_apply_spare_points = evaluate_movement_conditions(agv)

        if should_apply_spare_points:
            self._handle_spare_points(agv)
            can_move, _ = evaluate_movement_conditions(agv)

        return self._update_agv_movement_state(agv, can_move)

    def _handle_spare_points(self, agv: Agv) -> None:
        """Handle spare points application or removal."""
        if agv.spare_flag:
            remove_current_spare_point(agv)
        else:
            apply_for_spare_points(agv)

    def _update_agv_movement_state(self, agv: Agv, can_move: bool) -> Dict:
        """Update AGV state based on movement evaluation."""
        if can_move:
            agv.motion_state = AGVState.MOVING
            agv.reserved_node = agv.next_node
            agv.save()
            return {
                "success": True,
                "message": "AGV can move to next point",
                "state": "moving",
                "next_node": agv.next_node
            }

        agv.reserved_node = agv.current_node
        agv.save()
        return {
            "success": True,
            "message": "AGV must wait at current point",
            "state": "waiting"
        }

    def _create_error_response(self, message: str) -> Dict:
        """Create a standardized error response."""
        return {
            "success": False,
            "message": message
        }
