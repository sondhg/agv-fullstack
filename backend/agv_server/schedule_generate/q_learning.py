import numpy as np


class QLearning:
    def __init__(self, nodes, connections, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.nodes = nodes
        self.connections = connections
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = self._initialize_q_table()

    def _initialize_q_table(self):
        q_table = {}
        for node in self.nodes:
            q_table[node] = {
                neighbor: 0 for neighbor in self._get_neighbors(node)}
        return q_table

    def _get_neighbors(self, node):
        return [conn['node2'] for conn in self.connections if conn['node1'] == node]

    def train(self, start, end, episodes=1000):
        for _ in range(episodes):
            current_node = start
            while current_node != end:
                if np.random.rand() < self.epsilon:
                    # Explore: choose a random neighbor
                    next_node = np.random.choice(
                        self._get_neighbors(current_node))
                else:
                    # Exploit: choose the best action
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

    def _get_reward(self, current, next_node, end):
        if next_node == end:
            return 100  # High reward for reaching the destination
        return -1  # Small penalty for each step

    def get_shortest_path(self, start, end):
        path = [start]
        current_node = start
        while current_node != end:
            next_node = max(self.q_table[current_node],
                            key=self.q_table[current_node].get)
            path.append(next_node)
            current_node = next_node
        return path
