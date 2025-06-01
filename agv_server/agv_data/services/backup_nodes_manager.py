"""
Spare points management for AGV control policy.

This module implements the spare point allocation and management as described
in Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from typing import List
from ..models import Agv
from .algorithm4 import allocate_backup_nodes
from .utils import is_node_reserved_by_others
from .. import direction_to_turn


def _clear_backup_nodes(agv: Agv) -> None:
    """
    Helper method to reset backup nodes state for an AGV.

    Args:
        agv (Agv): The AGV object to reset spare points for
    """
    agv.spare_flag = False
    agv.backup_nodes = {}


def _get_all_other_remaining_paths(agv_id: int) -> List[List[int]]:
    """
    Helper method to get remaining paths of all other active AGVs.

    Args:
        agv_id (int): ID of the AGV to exclude

    Returns:
        List[List[int]]: List of remaining paths from other AGVs
    """
    paths = []
    for other_agv in Agv.objects.exclude(agv_id=agv_id):
        if other_agv.active_order:
            paths.append(other_agv.remaining_path)
    return paths


def apply_for_backup_nodes(agv: Agv) -> None:
    """
    Apply for spare points for an AGV's sequential shared points.

    This implements line 17 in Algorithm 2, which calls Algorithm 4
    for spare point allocation.

    Args:
        agv (Agv): The AGV object requiring spare points
    """
    if not agv.adjacent_common_nodes:
        _clear_backup_nodes(agv)
        return

    all_remaining_paths = _get_all_other_remaining_paths(agv.agv_id)
    backup_nodes = allocate_backup_nodes(agv.adjacent_common_nodes, all_remaining_paths)

    if backup_nodes:
        agv.spare_flag = True
        agv.backup_nodes = backup_nodes
    else:
        _clear_backup_nodes(agv)


def remove_current_backup_node(agv: Agv) -> None:
    """
    Remove the spare point allocated for the AGV's current position.
    According to Algorithm 2 lines 14-16, when F^i = 1, remove SP^i(v_c^i).

    Args:
        agv (Agv): The AGV object to remove current spare point from
    """
    if not agv.spare_flag or not agv.backup_nodes:
        return

    current_node_str = str(agv.current_node)
    if current_node_str in agv.backup_nodes:
        backup_nodes = agv.backup_nodes.copy()
        backup_nodes.pop(current_node_str, None)
        agv.backup_nodes = backup_nodes

        if not agv.backup_nodes:
            agv.spare_flag = False


def check_and_update_agvs_at_backup_nodes(agv_id: int) -> List[int]:
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
    backup_node_agvs = Agv.objects.filter(
        spare_flag=True,
        motion_state=Agv.WAITING
    ).exclude(agv_id=agv_id)

    for agv in backup_node_agvs:
        if not agv.active_order or not agv.remaining_path:
            continue

        next_node = agv.remaining_path[0]
        if not is_node_reserved_by_others(next_node, agv.agv_id):
            # Return AGV from spare point to main path
            agv.next_node = next_node
            agv.reserved_node = next_node
            agv.motion_state = Agv.MOVING

            # Calculate direction_change when returning from spare point
            if agv.previous_node:
                # Use direction_to_turn utility to calculate the direction change
                direction_change = direction_to_turn.get_action(
                    agv.previous_node,
                    agv.current_node,
                    next_node
                )

                # If get_action returns None, default to GO_STRAIGHT
                if direction_change is None:
                    direction_change = Agv.GO_STRAIGHT

                agv.direction_change = direction_change

                # Debug logging
                print(f"AGV {agv.agv_id} returning from spare point with direction_change={direction_change}, " +
                      f"previous={agv.previous_node}, current={agv.current_node}, next={next_node}")
            else:
                # If no previous_node, default to GO_STRAIGHT
                agv.direction_change = Agv.GO_STRAIGHT

            _clear_backup_nodes(agv)
            agv.save()
            updated_agvs.append(agv.agv_id)

    return updated_agvs
