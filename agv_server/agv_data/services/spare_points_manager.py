"""
Spare points management for AGV control policy.

This module implements the spare point allocation and management as described
in Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from typing import List
from ..models import Agv
from ..constants import AGVState
from .algorithm4 import allocate_spare_points
from .utils import is_node_reserved_by_others


def _clear_spare_points(agv: Agv) -> None:
    """
    Helper method to reset spare points state for an AGV.

    Args:
        agv (Agv): The AGV object to reset spare points for
    """
    agv.spare_flag = False
    agv.spare_points = {}


def _get_all_other_residual_paths(agv_id: int) -> List[List[int]]:
    """
    Helper method to get residual paths of all other active AGVs.

    Args:
        agv_id (int): ID of the AGV to exclude

    Returns:
        List[List[int]]: List of residual paths from other AGVs
    """
    paths = []
    for other_agv in Agv.objects.exclude(agv_id=agv_id):
        if other_agv.active_order:
            paths.append(other_agv.residual_path)
    return paths


def apply_for_spare_points(agv: Agv) -> None:
    """
    Apply for spare points for an AGV's sequential shared points.

    This implements line 17 in Algorithm 2, which calls Algorithm 4
    for spare point allocation.

    Args:
        agv (Agv): The AGV object requiring spare points
    """
    if not agv.scp:
        _clear_spare_points(agv)
        return

    all_residual_paths = _get_all_other_residual_paths(agv.agv_id)
    spare_points = allocate_spare_points(agv.scp, all_residual_paths)

    if spare_points:
        agv.spare_flag = True
        agv.spare_points = spare_points
    else:
        _clear_spare_points(agv)


def remove_current_spare_point(agv: Agv) -> None:
    """
    Remove the spare point allocated for the AGV's current position.
    According to Algorithm 2 lines 14-16, when F^i = 1, remove SP^i(v_c^i).

    Args:
        agv (Agv): The AGV object to remove current spare point from
    """
    if not agv.spare_flag or not agv.spare_points:
        return

    current_node_str = str(agv.current_node)
    if current_node_str in agv.spare_points:
        spare_points = agv.spare_points.copy()
        spare_points.pop(current_node_str, None)
        agv.spare_points = spare_points

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
    spare_point_agvs = Agv.objects.filter(
        spare_flag=True,
        motion_state=AGVState.WAITING
    ).exclude(agv_id=agv_id)

    for agv in spare_point_agvs:
        if not agv.active_order or not agv.residual_path:
            continue

        next_node = agv.residual_path[0]
        if not is_node_reserved_by_others(next_node, agv.agv_id):
            # Return AGV from spare point to main path
            agv.next_node = next_node
            agv.reserved_node = next_node
            agv.motion_state = AGVState.MOVING
            _clear_spare_points(agv)
            agv.save()
            updated_agvs.append(agv.agv_id)

    return updated_agvs
