import math
from .base import BasePathfinding


class GreedyDistance(BasePathfinding):
    """
    A simple greedy algorithm that always moves to the nearest unvisited neighbor.
    This is intentionally weak as it doesn't consider the overall path cost.
    """

    def __init__(self, nodes, connections):
        super().__init__(nodes, connections)
        self.graph = self._build_graph(connections)

    def _build_graph(self, connections):
        graph = {node: {} for node in self.nodes}
        for conn in connections:
            node1, node2, distance = conn["node1"], conn["node2"], conn["distance"]
            graph[node1][node2] = distance
            graph[node2][node1] = distance  # Assuming bidirectional paths
        return graph

    def find_shortest_path(self, start, end):
        """
        Greedy algorithm: always go to the nearest unvisited neighbor.
        This often gets stuck in local minima and produces suboptimal paths.
        """
        if start == end:
            return [start]

        current = start
        path = [current]
        visited = {current}

        while current != end:
            # Find the nearest unvisited neighbor
            min_distance = float('inf')
            next_node = None
            
            for neighbor, distance in self.graph[current].items():
                if neighbor not in visited and distance < min_distance:
                    min_distance = distance
                    next_node = neighbor

            # If no unvisited neighbors, we're stuck
            if next_node is None:
                # Try to backtrack or find any path to end
                for node in self.nodes:
                    if node not in visited and node in self.graph and end in self.graph[node]:
                        next_node = node
                        break
                
                if next_node is None:
                    return []  # No path found

            current = next_node
            path.append(current)
            visited.add(current)

            # Prevent infinite loops
            if len(path) > len(self.nodes):
                return []

        return path
