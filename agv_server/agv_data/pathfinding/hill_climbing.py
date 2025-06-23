import math
from .base import BasePathfinding


class HillClimbing(BasePathfinding):
    """Hill Climbing algorithm for pathfinding."""

    def __init__(self, nodes, connections):
        super().__init__(nodes, connections)
        self.graph = self._build_graph(connections)
        self.node_positions = self._generate_node_positions()

    def _build_graph(self, connections):
        """Build adjacency graph from connections."""
        graph = {node: {} for node in self.nodes}
        for conn in connections:
            node1, node2, distance = conn["node1"], conn["node2"], conn["distance"]
            graph[node1][node2] = distance
            graph[node2][node1] = distance  # Assuming bidirectional paths
        return graph

    def _generate_node_positions(self):
        """Generate pseudo-positions for nodes based on their connectivity."""
        # This is a simplified approach to estimate node positions
        # In a real scenario, you would have actual coordinates
        positions = {}
        num_nodes = len(self.nodes)
        
        # Arrange nodes in a grid-like pattern for distance estimation
        grid_size = int(math.ceil(math.sqrt(num_nodes)))
        
        for i, node in enumerate(self.nodes):
            x = i % grid_size
            y = i // grid_size
            positions[node] = (x, y)
            
        return positions

    def _euclidean_distance(self, node1, node2):
        """Calculate Euclidean distance between two nodes."""
        pos1 = self.node_positions[node1]
        pos2 = self.node_positions[node2]
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def find_shortest_path(self, start, end):
        """
        Find path using Hill Climbing algorithm.
        
        Hill Climbing always moves to the neighbor that is closest to the goal
        according to the heuristic function (Euclidean distance).
        """
        if start == end:
            return [start]
            
        if start not in self.graph or end not in self.graph:
            return []

        current = start
        path = [current]
        visited = set([current])
        max_iterations = len(self.nodes) * 2  # Prevent infinite loops
        iteration = 0

        while current != end and iteration < max_iterations:
            iteration += 1
            
            # Get all unvisited neighbors
            neighbors = []
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    heuristic = self._euclidean_distance(neighbor, end)
                    neighbors.append((heuristic, neighbor))
            
            if not neighbors:
                # No unvisited neighbors - we're stuck (local optimum)
                break
            
            # Sort neighbors by heuristic value (distance to goal)
            neighbors.sort(key=lambda x: x[0])
            
            # Choose the neighbor with the best (lowest) heuristic value
            best_neighbor = neighbors[0][1]
            
            current = best_neighbor
            path.append(current)
            visited.add(current)

        # Return path only if we reached the destination
        if current == end:
            return path
        else:
            return []  # Failed to find path (stuck in local optimum)
