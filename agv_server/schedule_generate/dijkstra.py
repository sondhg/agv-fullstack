import heapq
from map_data.models import Direction

# Define constants for cardinal directions
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4


class Dijkstra:
    """Dijkstra's algorithm for shortest path with detailed instructions."""

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

    def _get_direction(self, from_node, to_node):
        """
        Get the cardinal direction from one node to another.

        Args:
            from_node (int): The starting node.
            to_node (int): The destination node.

        Returns:
            int: The direction from `from_node` to `to_node`(`to_node` is to the north, east, south, or west of `from_node`):
                 NORTH, EAST, SOUTH, WEST.
                 Returns None if no direction is found in the `Direction` model.
        """
        try:
            return Direction.objects.get(node1=from_node, node2=to_node).direction
        except Direction.DoesNotExist:
            return None  # Return None if no direction is found

    def _get_action(self, prev_node, current_node, next_node):
        """
        Determine the action (direction change) based on three consecutive nodes.

        Args:
            prev_node (int): The previous node in the path.
            current_node (int): The current node in the path.
            next_node (int): The next node in the path.

        Returns:
            str: The action the AGV should take at the `current_node`:
                 - "none": No direction change (straight line).
                 - "right": Turn right.
                 - "left": Turn left.
                 - "reverse": Turn around (180 degrees).
        """
        # Get the directions from prev_node -> current_node and current_node -> next_node
        direction_to_current = self._get_direction(prev_node, current_node)
        direction_to_next = self._get_direction(current_node, next_node)

        if direction_to_current is None or direction_to_next is None:
            return "none"  # Default to "none" if direction data is missing

        # Determine the action based on the direction change
        if direction_to_current == direction_to_next:
            return "none"  # No direction change (straight line)
        elif (direction_to_current == NORTH and direction_to_next == EAST) or \
             (direction_to_current == EAST and direction_to_next == SOUTH) or \
             (direction_to_current == SOUTH and direction_to_next == WEST) or \
             (direction_to_current == WEST and direction_to_next == NORTH):
            return "right"  # Clockwise turn
        elif (direction_to_current == NORTH and direction_to_next == WEST) or \
             (direction_to_current == WEST and direction_to_next == SOUTH) or \
             (direction_to_current == SOUTH and direction_to_next == EAST) or \
             (direction_to_current == EAST and direction_to_next == NORTH):
            return "left"  # Counterclockwise turn
        elif (direction_to_current == NORTH and direction_to_next == SOUTH) or \
             (direction_to_current == SOUTH and direction_to_next == NORTH) or \
             (direction_to_current == EAST and direction_to_next == WEST) or \
             (direction_to_current == WEST and direction_to_next == EAST):
            return "reverse"  # Turn around (180 degrees)
        else:
            return "none"  # Default to "none" if 3 nodes are in a straight line

    def find_shortest_path(self, start, end):
        """
        Find the shortest path from the start node to the end node using Dijkstra's algorithm.

        Args:
            start (int): The starting node.
            end (int): The destination node.

        Returns:
            list: A list of tuples representing the instruction set for the path.
                  Each tuple is in the format (from_node, to_node, action).
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
                # Generate the full route including the return path
                # Reverse the path excluding the last node
                full_path = path + path[-2::-1]

                # Generate the instruction set
                instruction_set = []
                for i in range(1, len(full_path) - 1):
                    prev_node = full_path[i - 1]
                    current_node = full_path[i]
                    next_node = full_path[i + 1]
                    action = self._get_action(
                        prev_node, current_node, next_node)
                    instruction_set.append((prev_node, current_node, action))

                # Add the final segment to the instruction set
                instruction_set.append((full_path[-2], full_path[-1], "stop"))

                return instruction_set

            for neighbor, distance in self.graph[node].items():
                if neighbor not in visited:
                    heapq.heappush(
                        priority_queue, (cost + distance, neighbor, path))

        return []  # No path found
