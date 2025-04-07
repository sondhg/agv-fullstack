class SpCalculator:
    """Calculates SP (spare points) for sequential shared points."""

    def __init__(self, adjacency_matrix):
        """
        Initialize the SP calculator with the adjacency matrix.

        Args:
            adjacency_matrix (dict): A dictionary representing the adjacency matrix of the graph.
        """
        self.adjacency_matrix = adjacency_matrix

    def calculate_sp(self, scp, residual_paths):
        """
        Calculate spare points (SP) for sequential shared points (SCP).

        Args:
            scp (list): List of sequential shared points.
            residual_paths (list): List of residual paths for all AGVs.

        Returns:
            dict: A dictionary mapping SCP nodes to their spare points.
        """
        sp = {}

        # Flatten all residual paths into a single set
        occupied_points = set()
        for path in residual_paths:
            occupied_points.update(path)

        for point in scp:
            free_points = self._get_free_points(point, occupied_points)
            if free_points:
                # Assign the nearest free point (only the point, no distance)
                sp[point] = min(free_points)
            else:
                sp[point] = None  # No spare point available

        return sp

    def _get_free_points(self, point, occupied_points):
        """
        Get free points for a given point.

        Args:
            point (int): The point for which to find free points.
            occupied_points (set): Set of points currently occupied by AGVs.

        Returns:
            list: A list of free points.
        """
        free_points = []
        for neighbor in self.adjacency_matrix[point]:
            if neighbor not in occupied_points:
                free_points.append(neighbor)
        return free_points
