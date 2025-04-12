from .dijkstra import Dijkstra


class PathfindingFactory:
    """
    Factory class to create pathfinding algorithm instances.
    """

    @staticmethod
    def get_algorithm(algorithm_name, nodes, connections):
        """
        Get an instance of the specified pathfinding algorithm.

        Args:
            algorithm_name (str): The name of the algorithm ("dijkstra", "q_learning", "a_star").
            nodes (list): List of all nodes in the graph.
            connections (list): List of connections between nodes.

        Returns:
            BasePathfinding: An instance of the specified algorithm.
        """
        if algorithm_name == "dijkstra":
            return Dijkstra(nodes, connections)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
