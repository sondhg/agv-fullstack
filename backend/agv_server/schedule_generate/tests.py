from django.test import TestCase
from .q_learning import QLearning


class QLearningTestCase(TestCase):
    def setUp(self):
        self.nodes = [0, 1, 2, 3]
        self.connections = [
            {"node1": 0, "node2": 1, "distance": 1},
            {"node1": 1, "node2": 2, "distance": 1},
            {"node1": 2, "node2": 3, "distance": 1},
            {"node1": 0, "node2": 2, "distance": 2},
        ]
        self.q_learning = QLearning(self.nodes, self.connections)

    def test_shortest_path(self):
        self.q_learning.train(0, 3)
        path = self.q_learning.get_shortest_path(0, 3)
        self.assertEqual(path, [0, 1, 2, 3])  # Validate the shortest path