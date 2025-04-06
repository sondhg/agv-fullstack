class CpScpCalculator:
    """Calculates CP (shared points) and SCP (sequential shared points)."""

    def __init__(self, adjacency_matrix):
        self.adjacency_matrix = adjacency_matrix

    def calculate_cp_and_scp(self, all_paths):
        """
        Calculate shared points (CP) and sequential shared points (SCP) for all paths.

        Args:
            all_paths (list): List of paths for all AGVs.

        Returns:
            dict: A dictionary containing CP and SCP for each path.
        """
        cp = {}
        scp = {}

        # Step 1: Identify shared points (CP)
        for i, path in enumerate(all_paths):
            cp[i] = []
            for j, other_path in enumerate(all_paths):
                if i == j:
                    continue
                # Find shared points
                shared_points = set(path) & set(other_path)
                cp[i].extend(shared_points)

            cp[i] = sorted(set(cp[i]), key=path.index)  # Sort by path order

        # Step 2: Identify sequential shared points (SCP)
        for i, shared_points in cp.items():
            scp[i] = []
            for k in range(len(shared_points) - 1):
                v_p = shared_points[k]
                v_q = shared_points[k + 1]
                # Check adjacency using the adjacency matrix
                if v_q in self.adjacency_matrix[v_p]:
                    scp[i].append(v_p)
                    scp[i].append(v_q)

            # Remove duplicates while preserving order
            scp[i] = list(dict.fromkeys(scp[i]))

        return {"cp": cp, "scp": scp}
