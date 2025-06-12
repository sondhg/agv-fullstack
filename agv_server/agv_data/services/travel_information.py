"""
Travel information management for AGV control policy.

This module handles the updating of AGV travel information as described in
Algorithm 2 of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from ..models import Agv
from .utils import is_node_reserved_by_others


def update_travel_information(agv: Agv) -> None:
    """
    Update the travel information for an AGV based on its current position.
    This includes updating the next node in the remaining path.

    This function implements part of line 6 in Algorithm 2, specifically updating
    the traveling information I^i and determining the next node (v_n^i).

    Args:
        agv (Agv): The AGV object
    """
    remaining_path = agv.remaining_path

    # Debug logging
    print(f"DEBUG update_travel_information AGV {agv.agv_id}:")
    print(f"  current_node: {agv.current_node}")
    print(f"  remaining_path before update: {remaining_path}")

    if not remaining_path:
        # No remaining path, AGV should be at destination (workstation_node)
        print(f"  No remaining path - returning")
        return

    # Update the remaining path if the AGV has reached the first point in it
    if agv.current_node == remaining_path[0]:
        print(
            f"  AGV reached first node in remaining path ({remaining_path[0]}) - removing it")
        # Remove the current node from the remaining path as it's been visited
        # This implements Definition 2 from the algorithms-pseudocode.tex
        # "After an AGV reaches an identification point, the remaining path of the AGV is updated."
        remaining_path = remaining_path[1:]
        agv.remaining_path = remaining_path
        print(f"  remaining_path after update: {remaining_path}")
        agv.save()

    # Update next node (v_n^i) based on current position and remaining path
    if not remaining_path:
        # Remaining path is now empty, no next node
        agv.next_node = None
        print(f"  No remaining path - setting next_node to None")
    elif agv.current_node == remaining_path[0]:
        # This could happen if we didn't remove the current node from remaining path
        # Current node is the first in remaining path, next node is the second
        if len(remaining_path) > 1:
            agv.next_node = remaining_path[1]
            print(
                f"  Current node is first in path - setting next_node to {remaining_path[1]}")
        else:
            # This was the last point, no next node
            agv.next_node = None
            print(f"  Current node is last in path - setting next_node to None")
    else:
        # Current node is not in remaining path (e.g., after deadlock resolution or at a spare point)
        # Next node is the first in remaining path
        agv.next_node = remaining_path[0]
        print(
            f"  Current node not in path - setting next_node to {remaining_path[0]}")

        # Special case: If AGV is at a spare point, it should return to the main path
        # This implements the behavior described in Example 3 of the research paper
        if agv.spare_flag and not is_node_reserved_by_others(remaining_path[0], agv.agv_id):
            # The deadlock has been resolved, and the AGV can now return to its original path
            # According to Example 3: "r_3 satisfies Condition 1 after updating its traveling information,
            # and it will return to point 14. Then, set F_3 = 0, SP_3 = ∅"
            agv.spare_flag = False
            agv.backup_nodes = {}
            print(f"  AGV at spare point - clearing spare flags")
