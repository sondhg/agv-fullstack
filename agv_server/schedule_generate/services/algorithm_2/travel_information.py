"""
Travel information management for AGV control policy.

This module handles the updating of AGV travel information as described in
Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from agv_data.models import Agv
from schedule_generate.models import Schedule
from .utils import is_node_reserved_by_others


def update_travel_information(agv: Agv, schedule: Schedule) -> None:
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
        # Current node is not in residual path (e.g., after deadlock resolution or at a spare point)
        # Next node is the first in residual path
        agv.next_node = residual_path[0]

        # Special case: If AGV is at a spare point, it should return to the main path
        # This implements the behavior described in Example 3 of the research paper
        if agv.spare_flag and not is_node_reserved_by_others(residual_path[0], agv.agv_id):
            # The deadlock has been resolved, and the AGV can now return to its original path
            # According to Example 3: "r_3 satisfies Condition 1 after updating its traveling information,
            # and it will return to point 14. Then, set F_3 = 0, SP_3 = ∅"
            agv.spare_flag = False
            agv.spare_points = {}
