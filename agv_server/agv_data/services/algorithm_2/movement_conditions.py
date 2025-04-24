"""
Movement condition evaluation for AGV control policy.

This module implements the evaluation of movement conditions as described in Algorithm 2
of the DSPA algorithm from algorithms-pseudocode.tex.

The three conditions evaluated are:
1. v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
2. v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} and v_n^i ∉ {v_r^j, j ≠ i}
3. v_n^i ∈ SCP^i and ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0} but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}
"""
from typing import List, Tuple
from ...models import Agv
from .utils import is_node_reserved_by_others


def evaluate_movement_conditions(agv: Agv) -> Tuple[bool, bool, bool]:
    """
    Evaluate if an AGV can move based on Algorithm 2's conditions.

    According to the research paper:

    Condition 1: v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
    Condition 2: v_n^i ∈ SCP^i but ∀v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} 
                 and v_n^i ∉ {v_r^j, j ≠ i}
    Condition 3: v_n^i ∈ SCP^i and ∃v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0}
                 but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}

    Args:
        agv (Agv): The AGV to evaluate
        order (Order): The AGV's active order
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
    reserved_by_others = is_node_reserved_by_others(agv.next_node, agv.agv_id)

    if reserved_by_others:
        # Next point is reserved by another AGV, so AGV cannot move
        # None of the three conditions can be satisfied
        return False, False

    scp = agv.scp

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
    scp_with_no_spare_reservations = check_scp_with_no_spare_reservations(
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


def check_scp_with_no_spare_reservations(scp: List[int], exclude_agv_id: int) -> bool:
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
