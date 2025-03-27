import heapq


class Dijkstra:
    """Dijkstra's algorithm for shortest path."""

    def __init__(self, nodes, connections):
        """
        Initialize the Dijkstra object.

        Args:
            nodes (list): List of all nodes in the graph.
            connections (list): List of connections between nodes, where each connection
                                is a dictionary with keys "node1", "node2", and "distance".
        """
        self.nodes = nodes
        self.graph = self._build_graph(connections)

    def _build_graph(self, connections):
        """
        Build an adjacency list representation of the graph.

        Args:
            connections (list): List of connections between nodes.

        Returns:
            dict: A dictionary where each key is a node, and the value is another dictionary
                  of neighboring nodes and their distances.
        """
        graph = {node: {} for node in self.nodes}
        for conn in connections:
            node1, node2, distance = conn["node1"], conn["node2"], conn["distance"]
            graph[node1][node2] = distance
            graph[node2][node1] = distance  # Assuming bidirectional paths
        return graph

    def find_shortest_path(self, start, end):
        """
        Find the shortest path from the start node to the end node using Dijkstra's algorithm.

        Args:
            start (int): The starting node.
            end (int): The destination node.

        Returns:
            list: A list of nodes representing the shortest path.
        """
        priority_queue = [(0, start, [])]  # (cost, current_node, path)
        visited = set()

        while priority_queue:
            cost, node, path = heapq.heappop(priority_queue)

            if node in visited:
                continue
            visited.add(node)
            path = path + [node]

            if node == end:
                return path

            for neighbor, distance in self.graph[node].items():
                if neighbor not in visited:
                    heapq.heappush(
                        priority_queue, (cost + distance, neighbor, path))

        return []  # No path found
