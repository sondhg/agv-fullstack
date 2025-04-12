class SpCalculator:
    """
    Calculates SP (spare points) for sequential shared points.
    Implementation based on Algorithm 4 from the algorithms-pseudocode.tex.
    """

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
        Implementation of Algorithm 4 from the paper.

        Args:
            scp (list): List of sequential shared points.
            residual_paths (list): List of residual paths for all AGVs.

        Returns:
            dict: A dictionary mapping SCP nodes to their spare points, or empty if allocation fails.
        """
        if not scp:
            return {}
            
        # Create a combined set of points used in any residual path (occupied points)
        occupied_points = set()
        for path in residual_paths:
            if path:  # Skip empty paths
                occupied_points.update(path)
                
        # Calculate spare points for each point in SCP
        sp = {}
        
        # For each sequential shared point
        for point in scp:
            # Find free points for this shared point
            free_points = self._get_free_points(point, occupied_points)
            
            if free_points:
                # Choose the nearest free point (minimum distance)
                nearest_free_point = self._find_nearest_free_point(point, free_points)
                sp[str(point)] = nearest_free_point
            else:
                # If any point doesn't have free points, return empty set (allocation failed)
                return {}
                
        return sp
        
    def _get_free_points(self, point, occupied_points):
        """
        Get the set of free points linked to a point.
        These are points connected to 'point' but not in any residual path.
        
        Args:
            point (int): The point to find free points for.
            occupied_points (set): Set of points in any residual path.
            
        Returns:
            list: List of free points for the given point.
        """
        free_points = []
        
        # Get all neighboring points
        neighbors = self.adjacency_matrix.get(point, {})
        
        # Filter out occupied points
        for neighbor in neighbors:
            if neighbor not in occupied_points:
                free_points.append(neighbor)
                
        return free_points
        
    def _find_nearest_free_point(self, point, free_points):
        """
        Find the nearest free point among the available free points.
        
        Args:
            point (int): The reference point.
            free_points (list): List of free points to consider.
            
        Returns:
            int: The nearest free point (minimum distance).
        """
        if not free_points:
            return None
            
        if len(free_points) == 1:
            return free_points[0]
            
        # Find the free point with minimum distance
        min_distance = float('inf')
        nearest_point = None
        
        for fp in free_points:
            # Use the weight from adjacency matrix as distance
            distance = self.adjacency_matrix[point].get(fp, float('inf'))
            
            if distance < min_distance:
                min_distance = distance
                nearest_point = fp
                
        return nearest_point

    def _get_free_points_with_distance(self, point, occupied_points):
        """
        Get free points with their distances for a given point.

        Args:
            point (int): The point for which to find free points.
            occupied_points (set): Set of points currently occupied by AGVs.

        Returns:
            list: A list of tuples (free_point, distance).
        """
        free_points = []
        for neighbor in self.adjacency_matrix[point]:
            if neighbor not in occupied_points:
                # Use edge weight as distance if available, otherwise use 1 as default
                distance = self.adjacency_matrix[point].get(neighbor, 1)
                free_points.append((neighbor, distance))
        return free_points

    def find_nearest_free_point(self, point, occupied_points, visited=None):
        """
        Find the nearest free point using breadth-first search.
        This is a more thorough approach than just checking neighbors.

        Args:
            point (int): The starting point.
            occupied_points (set): Set of points currently occupied by AGVs.
            visited (set, optional): Set of visited points to prevent cycles.

        Returns:
            tuple: (nearest_free_point, distance) or None if no free point is found.
        """
        if visited is None:
            visited = set()
        
        # If current point is already free, return it with distance 0
        if point not in occupied_points and point not in visited:
            return (point, 0)
        
        visited.add(point)
        queue = [(point, 0)]  # (node, distance)
        while queue:
            current, distance = queue.pop(0)
            
            # Check neighbors
            for neighbor in self.adjacency_matrix[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    
                    # If neighbor is free, return it
                    if neighbor not in occupied_points:
                        return (neighbor, distance + 1)
                    
                    # Otherwise, add to queue for further exploration
                    queue.append((neighbor, distance + 1))
        
        return None  # No free point found
