"""
Implementation of Algorithm 4: Allocation of spare points for AGV r_i.

This algorithm handles allocation of spare points to resolve potential collisions and deadlocks between AGVs. When an AGV is about to enter its sequential shared points, it needs to allocate spare points first. This algorithm finds the nearest free point for each sequential shared point.
"""
from typing import Dict, List, Set, Optional
from map_data.models import Connection


def allocate_backup_nodes(adjacent_common_nodes: List[int], all_remaining_paths: List[List[int]]) -> Dict[str, int]:
    """
    Allocate backup nodes for an AGV's sequential shared points.

    Args:
        adjacent_common_nodes (List[int]): Adjacent common nodes (ACN^i) of the AGV
        all_remaining_paths (List[List[int]]): Remaining paths of all AGVs in the system

    Returns:
        Dict[str, int]: Mapping of shared points to their allocated backup nodes.
                       Empty dict if allocation fails.
    """
    # Convert remaining paths to a set for O(1) lookup
    occupied_points: Set[int] = set()
    for path in all_remaining_paths:
        occupied_points.update(path)

    backup_nodes: Dict[str, int] = {}

    # For each adjacent common node
    for adjacent_common_node in adjacent_common_nodes:
        # Get all neighboring points from the Connection model
        neighbors = get_free_points(adjacent_common_node, occupied_points)

        if not neighbors:
            # If no free points exist for any shared point, allocation fails
            return {}

        # Select the nearest free point as the backup node
        nearest_point = find_nearest_point(adjacent_common_node, neighbors)
        if nearest_point:
            # Store as string key for JSON serialization
            backup_nodes[str(adjacent_common_node)] = nearest_point
        else:
            # If we can't find a nearest point, allocation fails
            return {}

    return backup_nodes


def get_free_points(point: int, occupied_points: Set[int]) -> List[int]:
    """
    Get all free points connected to a given point.
    A point is free if it's not in any AGV's remaining path.

    Args:
        point (int): The point to find free neighbors for
        occupied_points (Set[int]): Set of points that appear in any AGV's remaining path

    Returns:
        List[int]: List of free points connected to the given point
    """
    # Get all connections where point is either node1 or node2
    connections = Connection.objects.filter(
        node1=point) | Connection.objects.filter(node2=point)

    free_points = []
    for conn in connections:
        # Get the other node of the connection
        neighbor = conn.node2 if conn.node1 == point else conn.node1
        # Add to free points if not in any remaining path
        if neighbor not in occupied_points:
            free_points.append(neighbor)

    return free_points


def find_nearest_point(adjacent_common_node: int, candidates: List[int]) -> Optional[int]:
    """
    Find the nearest point to a shared point from a list of candidates.
    Uses the Connection model's distance field to determine proximity.

    Args:
        adjacent_common_node (int): The shared point to find the nearest neighbor for
        candidates (List[int]): List of candidate points to check

    Returns:
        Optional[int]: The nearest point, or None if no valid point found
    """
    if not candidates:
        return None

    # Get connections for distance lookup
    min_distance = float('inf')
    nearest_point = None

    for candidate in candidates:
        # Try both orientations since Connection is undirected
        try:
            conn = Connection.objects.get(node1=adjacent_common_node, node2=candidate)
            distance = conn.distance
        except Connection.DoesNotExist:
            try:
                conn = Connection.objects.get(
                    node1=candidate, node2=adjacent_common_node)
                distance = conn.distance
            except Connection.DoesNotExist:
                # If no connection exists between these points, skip
                continue

        if distance < min_distance:
            min_distance = distance
            nearest_point = candidate

    return nearest_point
