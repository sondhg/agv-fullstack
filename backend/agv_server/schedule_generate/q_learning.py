import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


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

    def train(self, start, end, episodes=5000):
        epsilon = self.epsilon  # Initial exploration rate
        for episode in range(episodes):
            current_node = start
            while current_node != end:
                if np.random.rand() < epsilon:
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

            # Decay epsilon after each episode
            epsilon = max(0.01, epsilon * 0.99)  # Minimum epsilon is 0.01

            # # Log progress
            # if episode % 100 == 0:
            #     print(f"Episode {episode}: Current Q-table: {self.q_table}")

    def _get_reward(self, current, next_node, end):
        if next_node == end:
            return 100  # High reward for reaching the destination
        return -10  # Small penalty for each step

    def get_shortest_path(self, start, end):
        path = [start]
        current_node = start
        while current_node != end:
            next_node = max(self.q_table[current_node],
                            key=self.q_table[current_node].get)
            path.append(next_node)
            current_node = next_node
        return path

    # def visualize_q_table(self, filename="q_table_heatmap.png"):
    #     """Visualize the Q-table as a heatmap and save it in the specified folder."""
    #     # Convert the Q-table to a Pandas DataFrame
    #     data = []
    #     for current_node, actions in self.q_table.items():
    #         for next_node, q_value in actions.items():
    #             data.append([current_node, next_node, q_value])
    #     df = pd.DataFrame(
    #         data, columns=["Current Node", "Next Node", "Q-Value"])

    #     # Pivot the DataFrame to create a matrix for the heatmap
    #     pivot_table = df.pivot(index="Current Node",
    #                            columns="Next Node", values="Q-Value").fillna(0)

    #     # Plot the heatmap
    #     plt.figure(figsize=(10, 8))
    #     plt.title("Q-Table Heatmap")
    #     plt.xlabel("Next Node")
    #     plt.ylabel("Current Node")
    #     heatmap = plt.imshow(pivot_table, cmap="coolwarm",
    #                          interpolation="nearest")
    #     plt.colorbar(heatmap, label="Q-Value")
    #     plt.xticks(range(len(pivot_table.columns)),
    #                pivot_table.columns, rotation=90)
    #     plt.yticks(range(len(pivot_table.index)), pivot_table.index)

    #     # Save the heatmap as an image file
    #     # Ensure the folder exists
    #     folder_path = "media/q_table_heatmap"
    #     # Create the folder if it doesn't exist
    #     os.makedirs(folder_path, exist_ok=True)
    #     # Full path to save the file
    #     full_path = os.path.join(folder_path, filename)

    #     plt.savefig(full_path)
    #     plt.close()  # Close the plot to free up memory
    #     print(f"Q-table heatmap saved as {full_path}")
