import numpy as np
from .base import BasePathfinding


class QLearning(BasePathfinding):
    def __init__(self, nodes, connections, alpha=0.1, gamma=0.9, epsilon=0.1, episodes=1000):
        super().__init__(nodes, connections)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episodes = episodes
        self.q_table = self._initialize_q_table()
        self.distance_map = self._initialize_distance_map()

    def _initialize_q_table(self):
        return {node: {neighbor: 0 for neighbor in self._get_neighbors(node)} for node in self.nodes}

    def _initialize_distance_map(self):
        distance_map = {}
        for conn in self.connections:
            distance_map[(conn["node1"], conn["node2"])] = conn["distance"]
        return distance_map

    def _get_neighbors(self, node):
        return [conn["node2"] for conn in self.connections if conn["node1"] == node]

    def _get_reward(self, current_node, next_node, end):
        if next_node == end:
            return 100  # High reward for reaching the destination
        # Penalize distance
        return -self.distance_map.get((current_node, next_node), 1)

    def train(self, start, end):
        epsilon = self.epsilon
        for episode in range(self.episodes):
            current_node = start

            while current_node != end:
                neighbors = self._get_neighbors(current_node)
                if not neighbors:
                    break

                if np.random.rand() < epsilon:
                    next_node = np.random.choice(neighbors)
                else:
                    next_node = max(
                        self.q_table[current_node], key=self.q_table[current_node].get)

                reward = self._get_reward(current_node, next_node, end)
                best_future_q = max(
                    self.q_table[next_node].values(), default=0)

                self.q_table[current_node][next_node] += self.alpha * (
                    reward + self.gamma * best_future_q -
                    self.q_table[current_node][next_node]
                )

                current_node = next_node

            epsilon = max(0.01, epsilon * 0.99)

    def find_shortest_path(self, start, end):
        self.train(start, end)
        path = [start]
        current_node = start

        while current_node != end:
            if current_node not in self.q_table or not self.q_table[current_node]:
                return []

            next_node = max(self.q_table[current_node],
                            key=self.q_table[current_node].get)
            path.append(next_node)
            current_node = next_node

        return path
