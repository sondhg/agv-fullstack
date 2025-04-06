from django.test import TestCase
from .pathfinding.q_learning import QLearning


class QLearningTestCase(TestCase):
    def setUp(self):
        self.nodes = [0, 1, 2, 3, 4]
        self.connections = [
            {"node1": 0, "node2": 1, "distance": 1},
            {"node1": 1, "node2": 2, "distance": 1},
            {"node1": 2, "node2": 3, "distance": 1},
            {"node1": 3, "node2": 4, "distance": 1},
            {"node1": 0, "node2": 2, "distance": 2},
        ]
        self.q_learning = QLearning(self.nodes, self.connections)

    def test_complete_route(self):
        # Test the complete route: parking -> storage -> workstation -> parking
        parking_node = 0
        storage_node = 2
        workstation_node = 4

        path_to_storage = self.q_learning.find_shortest_path(
            parking_node, storage_node)
        path_to_workstation = self.q_learning.find_shortest_path(
            storage_node, workstation_node)
        path_back_to_parking = self.q_learning.find_shortest_path(
            workstation_node, parking_node)

        complete_path = (
            path_to_storage
            + path_to_workstation[1:]  # Avoid duplicate storage_node
            + path_back_to_parking[1:]  # Avoid duplicate workstation_node
        )

        # Validate the complete route
        self.assertEqual(complete_path, [0, 2, 3, 4, 3, 2, 0])
