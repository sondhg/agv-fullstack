"""
Main controller for AGV control policy.

This module implements the central controller's logic for managing AGV movement
based on Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.

The controller handles the high-level decision-making and delegates specific tasks
to specialized modules.
"""
from typing import Dict
from agv_data.models import Agv
from schedule_generate.models import Schedule
from schedule_generate.constants import AGVState
from .movement_conditions import evaluate_movement_conditions
from .travel_information import update_travel_information
from .spare_points_manager import apply_for_spare_points, remove_current_spare_point, check_and_update_agvs_at_spare_points
from .utils import is_node_reserved_by_others


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

            result_info = {}
            updated_agvs_list = []

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
                # Completed task, set AGV to idle
                return self._complete_agv_task(agv, schedule)
            else:
                # Update travel information (line 6 in Algorithm 2)
                update_travel_information(agv, schedule)

                # Special case: If AGV is at a spare point and the path is now clear,
                # prioritize returning to the main path
                if (agv.spare_flag and agv.next_node and
                        not is_node_reserved_by_others(agv.next_node, agv.agv_id)):
                    residual_path = schedule.residual_path
                    if residual_path and agv.next_node == residual_path[0]:
                        # The path is clear, AGV can move from spare point back to main path
                        result_info = self._return_agv_from_spare_point(agv)
                    else:
                        # Standard movement evaluation
                        result_info = self._evaluate_and_update_agv_movement(
                            agv, schedule)
                else:
                    # Standard movement evaluation
                    result_info = self._evaluate_and_update_agv_movement(
                        agv, schedule)

            # Check if other AGVs at spare points can return to their paths
            if agv.motion_state == AGVState.MOVING:
                updated_agvs_list = check_and_update_agvs_at_spare_points(
                    agv_id)

            # Add information about updated AGVs to the result
            if updated_agvs_list:
                result_info["updated_agvs"] = updated_agvs_list
                result_info["message"] += f". Also updated AGVs {updated_agvs_list} to return from spare points."

            return result_info

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

    def _complete_agv_task(self, agv: Agv, schedule: Schedule) -> Dict:
        """
        Complete the current task for an AGV that has reached its workstation node.

        Args:
            agv (Agv): The AGV object
            schedule (Schedule): The AGV's active schedule

        Returns:
            Dict: Result information indicating task completion
        """
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

    def _return_agv_from_spare_point(self, agv: Agv) -> Dict:
        """
        Move an AGV from its spare point back to its original path.

        Args:
            agv (Agv): The AGV object

        Returns:
            Dict: Result information about the AGV's movement
        """
        # Clear spare point flags since AGV is returning to main path
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

    def _evaluate_and_update_agv_movement(self, agv: Agv, schedule: Schedule) -> Dict:
        """
        Evaluate movement conditions and update AGV state accordingly.

        Args:
            agv (Agv): The AGV object
            schedule (Schedule): The AGV's active schedule

        Returns:
            Dict: Result information about the AGV's movement decision
        """
        # Evaluate movement conditions
        can_move, should_apply_spare_points = evaluate_movement_conditions(
            agv, schedule)

        # If AGV needs to apply for spare points
        if should_apply_spare_points:
            # If spare_flag is already set, just remove current spare point
            if agv.spare_flag:
                remove_current_spare_point(agv)
            else:
                # Apply for spare points
                apply_for_spare_points(agv, schedule)

            # Re-evaluate movement conditions after spare point application
            can_move, _ = evaluate_movement_conditions(agv, schedule)

        # Update AGV state based on evaluation result
        if can_move:
            # AGV can move
            agv.motion_state = AGVState.MOVING
            agv.reserved_node = agv.next_node
            agv.save()
            return {
                "success": True,
                "message": "AGV can move to next point",
                "state": "moving",
                "next_node": agv.next_node
            }
        else:
            # AGV must wait
            agv.reserved_node = agv.current_node
            agv.save()
            return {
                "success": True,
                "message": "AGV must wait at current point",
                "state": "waiting"
            }
