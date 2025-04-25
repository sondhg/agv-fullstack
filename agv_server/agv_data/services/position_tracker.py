"""
Position tracker for AGV movement.

This module handles tracking an AGV's position history, specifically managing
the previous_node field which stores the last position of an AGV before its current position.
This is not part of the DSPA algorithm but is useful for determining turn directions.
"""
from ..models import Agv


def update_previous_node(agv: Agv) -> None:
    """
    Updates the previous_node field of an AGV when its current_node changes.

    This function should be called after an AGV's current_node has been updated
    but before the new position is saved to the database. It takes the current
    value of current_node and saves it as previous_node.

    Args:
        agv (Agv): The AGV object whose previous_node needs to be updated
    """
    # Only update previous_node if current_node exists and has changed
    if agv.current_node is not None and agv.current_node != agv.previous_node:
        # Store the current node value as the previous node
        agv.previous_node = agv.current_node
        # Note: We don't call agv.save() here as that will be done by the caller


def get_previous_position(agv_id: int) -> int:
    """
    Get the previous position of an AGV.

    Args:
        agv_id (int): The ID of the AGV

    Returns:
        int: The previous node ID or None if not available
    """
    try:
        agv = Agv.objects.get(agv_id=agv_id)
        return agv.previous_node
    except Agv.DoesNotExist:
        return None
