import numpy as np


class QLearning:
    def __init__(self, nodes, connections, alpha=0.1, gamma=0.9, epsilon=0.1, episodes=1000):
        self.nodes = nodes
        self.connections = connections
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.episodes = episodes  # Reduce to optimize performance
        self.q_table = self._initialize_q_table()
        self.distance_map = self._initialize_distance_map()

    def _initialize_q_table(self):
        return {node: {neighbor: 0 for neighbor in self._get_neighbors(node)} for node in self.nodes}

    def _initialize_distance_map(self):
        """Creates a dictionary storing distances between connected nodes."""
        distance_map = {}
        for conn in self.connections:
            distance_map[(conn["node1"], conn["node2"])] = conn["distance"]
        return distance_map

    def _get_neighbors(self, node):
        return [conn["node2"] for conn in self.connections if conn["node1"] == node]

    def _get_reward(self, current, next_node, end):
        """Returns a negative reward (penalty) based on distance to encourage shorter paths."""
        if next_node == end:
            return 100  # Large reward for reaching destination
        # Negative distance penalty
        return -self.distance_map.get((current, next_node), 10)

    def train(self, start, end):
        epsilon = self.epsilon  # Initial exploration rate
        for episode in range(self.episodes):
            current_node = start

            while current_node != end:
                neighbors = self._get_neighbors(current_node)
                if not neighbors:
                    break  # No valid moves, stop training

                # Choose action (next node)
                if np.random.rand() < epsilon:
                    next_node = np.random.choice(neighbors)  # Explore
                else:
                    next_node = max(
                        # Exploit
                        self.q_table[current_node], key=self.q_table[current_node].get)

                # Get reward
                reward = self._get_reward(current_node, next_node, end)
                best_future_q = max(
                    self.q_table[next_node].values(), default=0)

                # Update Q-table
                self.q_table[current_node][next_node] += self.alpha * (
                    reward + self.gamma * best_future_q -
                    self.q_table[current_node][next_node]
                )

                current_node = next_node

            # Decay epsilon for better convergence
            epsilon = max(0.01, epsilon * 0.99)  # Minimum epsilon = 0.01

    def get_shortest_path(self, start, end):
        """Finds the path with the highest Q-values"""
        path = [start]
        current_node = start

        while current_node != end:
            if current_node not in self.q_table or not self.q_table[current_node]:
                return []  # No valid path found

            next_node = max(self.q_table[current_node],
                            key=self.q_table[current_node].get)
            path.append(next_node)
            current_node = next_node

        # Append the reversed path back to the start_point
        return path + path[-2::-1]  # Reverse the path excluding the last node
