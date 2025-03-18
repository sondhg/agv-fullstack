import heapq


class Dijkstra:
    """Dijkstra's algorithm for shortest path."""

    def __init__(self, nodes, connections):
        self.nodes = nodes
        self.graph = self._build_graph(connections)

    def _build_graph(self, connections):
        """Build an adjacency list with distances."""
        graph = {node: {} for node in self.nodes}
        for conn in connections:
            node1, node2, distance = conn["node1"], conn["node2"], conn["distance"]
            graph[node1][node2] = distance
            graph[node2][node1] = distance  # Assuming bidirectional paths
        return graph

    def find_shortest_path(self, start, end):
        """Dijkstra's algorithm for shortest path."""
        priority_queue = [(0, start, [])]  # (cost, current_node, path)
        visited = set()

        while priority_queue:
            cost, node, path = heapq.heappop(priority_queue)

            if node in visited:
                continue
            visited.add(node)
            path = path + [node]

            if node == end:
                # # ! Shortest path from start_point to end_point
                # return path

                # ! Append the reversed path back to the start_point
                # Reverse the path excluding the last node
                return path + path[-2::-1]

            for neighbor, distance in self.graph[node].items():
                if neighbor not in visited:
                    heapq.heappush(
                        priority_queue, (cost + distance, neighbor, path))

        return []  # No path found
