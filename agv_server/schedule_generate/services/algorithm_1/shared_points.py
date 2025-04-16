"""
Shared points calculation module for the DSPA algorithm.
"""
from typing import List, Set, Dict


class SharedPointsCalculator:
    """Handles calculation of shared points (CP) and sequential shared points (SCP)."""

    def __init__(self, connections: List[Dict]):
        """
        Initialize the calculator with map connections.

        Args:
            connections (List[Dict]): List of node connections from the map.
        """
        self.connections = connections
        self.adjacent_points = self._build_adjacency_map()

    def _build_adjacency_map(self) -> Dict[int, Set[int]]:
        """
        Build a map of adjacent points for faster lookups.
        
        Returns:
            Dict[int, Set[int]]: Map of node to its adjacent nodes.
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

    def calculate_shared_points(self, current_path: list, other_paths: List[List]) -> list:
        """
        Calculate the shared points (CP^i) for a path based on Definition 3.
        For an active AGV r_i, CP^i consists of an ordered sequence of points shared with other AGVs:
        CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}

        Args:
            current_path (list): The path to calculate shared points for (Π_i)
            other_paths (List[List]): List of other residual paths to compare against (Π_j, j ≠ i)

        Returns:
            list: List of shared points in order of appearance in current_path
        """
        # Create a set of all points in other paths for O(1) lookup
        all_other_path_points = set()
        for path in other_paths:
            all_other_path_points.update(path)

        # Return points that exist in other paths, maintaining original order
        return [point for point in current_path if point in all_other_path_points]

    def calculate_sequential_shared_points(self, shared_points: list) -> list:
        """
        Calculate sequential shared points (SCP^i) based on Definition 4 from the paper.
        Returns shared points that form sequences of connected points.

        Definition 4: For AGV r_i, its sequential shared points can be denoted as
        SCP^i = {v_p : D(v_p, v_q) ≠ 0, v_p ∈ CP^i, v_q ∈ CP^i}
        where v_q and v_p are the shared points of r_i, and D is the adjacency matrix.

        Args:
            shared_points (list): List of shared points to analyze

        Returns:
            list: List of sequential shared points in order of appearance
        """
        if len(shared_points) <= 1:
            return []

        shared_points_set = set(shared_points)
        sequential_points = []

        for point in shared_points:
            if point not in self.adjacent_points:
                continue

            # Check if point has any adjacent shared points
            if any(adj_point in shared_points_set for adj_point in self.adjacent_points[point]):
                sequential_points.append(point)

        # Return points in original order
        return [p for p in shared_points if p in sequential_points]