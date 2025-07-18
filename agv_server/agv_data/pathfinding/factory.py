"""
Factory class for creating pathfinding algorithm instances.
"""

from .dijkstra import Dijkstra
from .greedy import GreedyDistance
from .hill_climbing import HillClimbing


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
            algorithm_name (str): The name of the algorithm ("dijkstra", "greedy", "hill_climbing").
            nodes (list): List of all nodes in the graph.
            connections (list): List of connections between nodes.

        Returns:
            BasePathfinding: An instance of the specified algorithm.

        Raises:
            ValueError: If the specified algorithm is not supported.
        """
        algorithms = {
            "dijkstra": Dijkstra,
            "greedy": GreedyDistance,
            "hill_climbing": HillClimbing,
        }

        if algorithm_name in algorithms:
            return algorithms[algorithm_name](nodes, connections)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")

    @staticmethod
    def get_available_algorithms():
        """Get list of available algorithm names."""
        return ["dijkstra", "greedy", "hill_climbing"]
