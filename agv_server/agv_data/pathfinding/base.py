from abc import ABC, abstractmethod


class BasePathfinding(ABC):
    """
    Abstract base class for all pathfinding algorithms.
    """

    def __init__(self, nodes, connections):
        """
        Initialize the pathfinding algorithm.

        Args:
            nodes (list): List of all nodes in the graph.
            connections (list): List of connections between nodes.
        """
        self.nodes = nodes
        self.connections = connections

    @abstractmethod
    def find_shortest_path(self, start, end):
        """
        Find the shortest path from the start node to the end node.

        Args:
            start (int): The starting node.
            end (int): The destination node.

        Returns:
            list: A list of nodes representing the shortest path.
        """
        pass
