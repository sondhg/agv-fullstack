"""
Algorithm 4 from research paper: Allocation of spare points for AGV r_i.
When an AGV is about to enter its sequential shared points, it needs to allocate
spare points first. This algorithm finds the nearest free point for each sequential shared point.
"""
from typing import Dict, List, Set, Optional
from map_data.models import Connection


def allocate_spare_points(scp: List[int], all_residual_paths: List[List[int]]) -> Dict[str, int]:
    """
    Allocate spare points for an AGV's sequential shared points.

    Args:
        scp (List[int]): Sequential shared points (SCP^i) of the AGV
        all_residual_paths (List[List[int]]): Residual paths of all AGVs in the system

    Returns:
        Dict[str, int]: Mapping of shared points to their allocated spare points.
                       Empty dict if allocation fails.
    """
    # Convert residual paths to a set for O(1) lookup
    occupied_points: Set[int] = set()
    for path in all_residual_paths:
        occupied_points.update(path)

    spare_points: Dict[str, int] = {}

    # For each sequential shared point
    for shared_point in scp:
        # Get all neighboring points from the Connection model
        neighbors = get_free_points(shared_point, occupied_points)

        if not neighbors:
            # If no free points exist for any shared point, allocation fails
            return {}

        # Select the nearest free point as the spare point
        nearest_point = find_nearest_point(shared_point, neighbors)
        if nearest_point:
            # Store as string key for JSON serialization
            spare_points[str(shared_point)] = nearest_point
        else:
            # If we can't find a nearest point, allocation fails
            return {}

    return spare_points


def get_free_points(point: int, occupied_points: Set[int]) -> List[int]:
    """
    Get all free points connected to a given point.
    A point is free if it's not in any AGV's residual path.

    Args:
        point (int): The point to find free neighbors for
        occupied_points (Set[int]): Set of points that appear in any AGV's residual path

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
        # Add to free points if not in any residual path
        if neighbor not in occupied_points:
            free_points.append(neighbor)

    return free_points


def find_nearest_point(shared_point: int, candidates: List[int]) -> Optional[int]:
    """
    Find the nearest point to a shared point from a list of candidates.
    Uses the Connection model's distance field to determine proximity.

    Args:
        shared_point (int): The shared point to find the nearest neighbor for
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
            conn = Connection.objects.get(node1=shared_point, node2=candidate)
            distance = conn.distance
        except Connection.DoesNotExist:
            try:
                conn = Connection.objects.get(node1=candidate, node2=shared_point)
                distance = conn.distance
            except Connection.DoesNotExist:
                # If no connection exists between these points, skip
                continue

        if distance < min_distance:
            min_distance = distance
            nearest_point = candidate

    return nearest_point
