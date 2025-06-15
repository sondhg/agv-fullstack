"""
Shared points calculation module for the DSPA algorithm.

This module implements the shared points calculation aspects of Algorithm 1
from the research paper.
"""
from typing import List, Dict, Set, Optional
from map_data.models import Connection
from ..models import Agv


class CommonNodesCalculator:
    """
    Handles calculation of shared points between AGVs' paths.

    This class implements the shared points calculation logic from Algorithm 1
    in the DSPA algorithm, handling CP and SCP calculations.
    """

    def __init__(self, connections):
        """
        Initialize the CommonNodesCalculator: with map connections.

        Args:
            connections (List[Dict]): List of connection dictionaries with node1, node2, and distance
        """
        self.connections = connections
        # Build adjacency map for sequential shared points calculation
        self.adjacent_points = self._build_adjacency_map()

    def _build_adjacency_map(self) -> Dict[int, Set[int]]:
        """
        Build an adjacency map from the connections for efficient lookup.

        Returns:
            Dict[int, Set[int]]: Mapping of nodes to their adjacent nodes
        """
        adjacent_points = {}
        for conn in self.connections:
            node1, node2 = conn['node1'], conn['node2']
            if node1 not in adjacent_points:
                adjacent_points[node1] = set()
            if node2 not in adjacent_points:
                adjacent_points[node2] = set()
            adjacent_points[node1].add(node2)
            adjacent_points[node2].add(node1)
        return adjacent_points

    def calculate_common_nodes(self, current_path: List[int], other_paths: List[List[int]]) -> List[int]:
        """
        Calculate the common nodes (CP^i) for a path based on Definition 3.
        For an active AGV r_i, CP^i consists of an ordered sequence of points shared with other AGVs:
        CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}

        Args:
            current_path (List[int]): The path to calculate common nodes for (Π_i)
            other_paths (List[List[int]]): List of other remaining paths to compare against (Π_j, j ≠ i)

        Returns:
            List[int]: List of common nodes in order of appearance in current_path
        """
        if not current_path:
            return []

        # Create a set of all points in other paths for O(1) lookup
        all_other_path_points = set()
        for path in other_paths:
            all_other_path_points.update(path)

        # Return points that exist in both current path and other paths, maintaining original order
        return [point for point in current_path if point in all_other_path_points]

    def calculate_sequential_common_nodes(self, common_nodes: List[int]) -> List[int]:
        """
        Calculate sequential shared points (SCP^i) based on Definition 4 from the paper.
        Returns shared points that form sequences of connected points.

        Definition 4: For AGV r_i, its sequential shared points can be denoted as
        SCP^i = {v_p : D(v_p, v_q) ≠ 0, v_p ∈ CP^i, v_q ∈ CP^i}
        where v_q and v_p are the shared points of r_i, and D is the adjacency matrix.

        Args:
            common_nodes (List[int]): List of shared points to analyze

        Returns:
            List[int]: List of sequential shared points in order of appearance
        """
        if len(common_nodes) <= 1:
            return []

        common_nodes_set = set(common_nodes)
        sequential_points = []

        for point in common_nodes:
            if point not in self.adjacent_points:
                continue

            # Check if point has any adjacent shared points
            if any(adj_point in common_nodes_set for adj_point in self.adjacent_points[point]):
                sequential_points.append(point)

        # Return points in original order
        return [p for p in common_nodes if p in sequential_points]


def update_common_nodes(agv: Agv) -> None:
    """
    Update shared points (CP) and sequential shared points (SCP) for an AGV.

    Args:
        agv (Agv): The AGV to update shared points for
    """
    # Get all other AGVs' remaining paths
    other_paths = []
    other_agvs = Agv.objects.filter(
        active_order__isnull=False).exclude(agv_id=agv.agv_id)

    for other_agv in other_agvs:
        if other_agv.remaining_path:
            other_paths.append(other_agv.remaining_path)

    # Calculate shared points
    common_nodes = calculate_common_nodes(agv.remaining_path, other_paths)

    # Update AGV's common_nodes field
    agv.common_nodes = common_nodes

    # Calculate sequential shared points
    sequential_common_nodes = calculate_sequential_common_nodes(common_nodes)

    # Update AGV's adjacent_common_nodes field
    agv.adjacent_common_nodes = sequential_common_nodes

    agv.save()


def calculate_common_nodes(current_path: List[int], other_paths: List[List[int]]) -> List[int]:
    """
    Calculate the shared points (CP^i) for a path based on Definition 3.
    For an active AGV r_i, CP^i consists of an ordered sequence of points shared with other AGVs:
    CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}

    Args:
        current_path (List[int]): The path to calculate shared points for (Π_i)
        other_paths (List[List[int]]): List of other remaining paths to compare against (Π_j, j ≠ i)

    Returns:
        List[int]: List of shared points in order of appearance in current_path
    """
    if not current_path:
        return []

    # Create a set of all points in other paths for O(1) lookup
    all_other_path_points = set()
    for path in other_paths:
        all_other_path_points.update(path)

    # Return points that exist in both current path and other paths, maintaining original order
    return [point for point in current_path if point in all_other_path_points]


def calculate_sequential_common_nodes(common_nodes: List[int]) -> List[int]:
    """
    Calculate sequential shared points (SCP^i) based on Definition 4 from the paper.
    Returns shared points that form sequences of connected points.

    Definition 4: For AGV r_i, its sequential shared points can be denoted as
    SCP^i = {v_p : D(v_p, v_q) ≠ 0, v_p ∈ CP^i, v_q ∈ CP^i}
    where v_q and v_p are the shared points of r_i, and D is the adjacency matrix.

    Args:
        common_nodes (List[int]): List of shared points to analyze

    Returns:
        List[int]: List of sequential shared points in order of appearance
    """
    if len(common_nodes) <= 1:
        return []

    # Get all connections from the database
    connections = Connection.objects.all().values('node1', 'node2')

    # Build adjacency map
    adjacent_points = {}
    for conn in connections:
        node1, node2 = conn['node1'], conn['node2']
        if node1 not in adjacent_points:
            adjacent_points[node1] = set()
        if node2 not in adjacent_points:
            adjacent_points[node2] = set()
        adjacent_points[node1].add(node2)
        adjacent_points[node2].add(node1)

    common_nodes_set = set(common_nodes)
    sequential_points = []

    for point in common_nodes:
        if point not in adjacent_points:
            continue

        # Check if point has any adjacent shared points
        if any(adj_point in common_nodes_set for adj_point in adjacent_points[point]):
            sequential_points.append(point)

    # Return points in original order
    return [p for p in common_nodes if p in sequential_points]


def recalculate_all_common_nodes(log_summary: bool = False) -> None:
    """
    Recalculate common nodes and adjacent common nodes for all AGVs with active orders.
    This function should be called whenever a new order is assigned to an AGV,
    as it may affect the common nodes of all other active AGVs.

    Args:
        log_summary: Whether to log a detailed summary after recalculation
    """
    try:
        # Get all AGVs with active orders
        active_agvs = Agv.objects.filter(active_order__isnull=False)

        if not active_agvs.exists():
            return

        # Get connections for adjacency calculations
        connections = []
        for conn in Connection.objects.values():
            connections.append({
                'node1': int(conn['node1']),
                'node2': int(conn['node2']),
                'distance': conn['distance']
            })

        # Initialize the common nodes calculator
        calculator = CommonNodesCalculator(connections)

        # For each active AGV, recalculate its common nodes
        for agv in active_agvs:
            if not agv.remaining_path:
                agv.common_nodes = []
                agv.adjacent_common_nodes = []
                agv.save(update_fields=['common_nodes',
                         'adjacent_common_nodes'])
                continue

            # Get all other active AGVs' remaining paths
            other_paths = []
            other_agvs = active_agvs.exclude(agv_id=agv.agv_id)

            for other_agv in other_agvs:
                if other_agv.remaining_path:
                    other_paths.append(other_agv.remaining_path)

            # Calculate common nodes and adjacent common nodes
            common_nodes = calculator.calculate_common_nodes(
                agv.remaining_path, other_paths)
            adjacent_common_nodes = calculator.calculate_sequential_common_nodes(
                common_nodes)
            # Update the AGV
            agv.common_nodes = common_nodes
            agv.adjacent_common_nodes = adjacent_common_nodes
            agv.save(update_fields=['common_nodes', 'adjacent_common_nodes'])

        print(
            f"Successfully recalculated common nodes for {active_agvs.count()} active AGVs")

        # Log summary if requested
        if log_summary:
            log_common_nodes_summary()

    except Exception as e:
        print(f"Error recalculating common nodes for all AGVs: {str(e)}")
        import traceback
        traceback.print_exc()


def log_common_nodes_summary() -> None:
    """
    Log a summary of common nodes for all active AGVs.
    Useful for debugging and monitoring the path planning system.
    """
    try:
        active_agvs = Agv.objects.filter(active_order__isnull=False)

        if not active_agvs.exists():
            print("No active AGVs found for common nodes summary")
            return

        print(
            f"\n=== Common Nodes Summary for {active_agvs.count()} Active AGVs ===")

        for agv in active_agvs:
            common_count = len(agv.common_nodes) if agv.common_nodes else 0
            adjacent_count = len(
                agv.adjacent_common_nodes) if agv.adjacent_common_nodes else 0
            path_length = len(agv.remaining_path) if agv.remaining_path else 0

            print(
                f"AGV {agv.agv_id}: Path Length={path_length}, Common Nodes={common_count}, Adjacent Common={adjacent_count}")

            if agv.common_nodes:
                print(f"  Common nodes: {agv.common_nodes}")
            if agv.adjacent_common_nodes:
                print(f"  Adjacent common nodes: {agv.adjacent_common_nodes}")

        print("=" * 50)

    except Exception as e:
        print(f"Error generating common nodes summary: {str(e)}")
