from .base import BasePathfinding


class GreedyDistance(BasePathfinding):
    """Greedy algorithm that always moves to the closest unvisited neighbor - often suboptimal."""

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
        Greedy approach: always move to the closest unvisited neighbor.
        This often leads to suboptimal paths.
        """
        if start == end:
            return [start]
        
        current = start
        path = [start]
        visited = set([start])
        
        while current != end:
            neighbors = [(neighbor, dist) for neighbor, dist in self.graph[current].items() 
                        if neighbor not in visited]
            
            if not neighbors:
                # Dead end - this greedy approach can get stuck
                return []
            
            # Choose the closest neighbor (greedy choice)
            next_node = min(neighbors, key=lambda x: x[1])[0]
            path.append(next_node)
            visited.add(next_node)
            current = next_node
            
            # Prevent infinite loops
            if len(path) > len(self.nodes):
                return []
        
        return path
