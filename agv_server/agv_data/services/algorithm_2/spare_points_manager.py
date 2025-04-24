"""
Spare points management for AGV control policy.

This module implements the spare point allocation and management as described
in Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from typing import List
from ...models import Agv, AGV_STATE_MOVING, AGV_STATE_WAITING
from ..algorithm_4.algorithm4 import allocate_spare_points
from .utils import is_node_reserved_by_others


def apply_for_spare_points(agv: Agv) -> None:
    """
    Apply for spare points for an AGV's sequential shared points.

    This implements line 17 in Algorithm 2, which calls Algorithm 4
    for spare point allocation.

    Args:
        agv (Agv): The AGV object
    """

    scp = agv.scp

    if not scp:
        # No sequential shared points, no need for spare points
        agv.spare_flag = False
        agv.spare_points = {}
        return

    # Get all residual paths of other AGVs
    all_residual_paths = []
    for other_agv in Agv.objects.exclude(agv_id=agv.agv_id):
        if other_agv.active_order:
            all_residual_paths.append(
                other_agv.residual_path)

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


def remove_current_spare_point(agv: Agv) -> None:
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


def check_and_update_agvs_at_spare_points(agv_id: int) -> List[int]:
    """
    Check and update AGVs that are at spare points and may need to return to their original path.

    This handles the special case in Example 3 of the research paper where r_3 returns
    from spare point 6 back to node 14 as soon as r_2 moves to node 14 (rather than node 22).
    The AGV at a spare point should return to its path as soon as its original next node is free.

    Args:
        agv_id (int): The ID of the AGV that just updated its position

    Returns:
        List[int]: IDs of AGVs that were updated to return from spare points
    """

    updated_agvs = []

    # Find all AGVs that are at spare points (spare_flag=True) and in waiting state
    spare_point_agvs = Agv.objects.filter(
        spare_flag=True,
        motion_state=AGV_STATE_WAITING
    ).exclude(agv_id=agv_id)

    # For each AGV at a spare point
    for agv in spare_point_agvs:
        if not agv.active_order:
            continue

        # Get the residual path and next node
        residual_path = agv.residual_path
        if not residual_path:
            continue

        # Check if the next node in the residual path is now free
        next_node = residual_path[0]  # First node in residual path
        if not is_node_reserved_by_others(next_node, agv.agv_id):
            # The path is clear, AGV can return from spare point to main path
            agv.next_node = next_node
            agv.spare_flag = False
            agv.spare_points = {}
            agv.motion_state = AGV_STATE_MOVING
            agv.reserved_node = next_node
            agv.save()
            updated_agvs.append(agv.agv_id)

    return updated_agvs
