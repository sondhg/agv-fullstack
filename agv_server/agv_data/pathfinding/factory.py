"""
Factory class for creating pathfinding algorithm instances.
"""
from .dijkstra import Dijkstra


class PathfindingFactory:
    """
    Factory class to create pathfinding algorithm instances.

    This factory pattern allows for easily switching between different
    pathfinding algorithms while maintaining a consistent interface.
    """

    @staticmethod
    def get_algorithm(algorithm_name, nodes, connections):
        """
        Get an instance of the specified pathfinding algorithm.

        Args:
            algorithm_name (str): The name of the algorithm ("dijkstra", "a_star", etc.).
            nodes (list): List of all nodes in the graph.
            connections (list): List of connections between nodes.

        Returns:
            BasePathfinding: An instance of the specified algorithm.

        Raises:
            ValueError: If the specified algorithm is not supported.
        """
        if algorithm_name == "dijkstra":
            return Dijkstra(nodes, connections)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
