"""
Utility functions for AGV control policy.

This module provides helper functions for the Algorithm 2 implementation.
"""
from ...models import Agv


def is_node_reserved_by_others(node: int, exclude_agv_id: int) -> bool:
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
