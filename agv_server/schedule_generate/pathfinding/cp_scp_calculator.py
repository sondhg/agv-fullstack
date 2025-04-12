class CpScpCalculator:
    """
    Calculates CP (shared points) and SCP (sequential shared points).
    Implementation based on Definition 3 and 4 from the algorithms-pseudocode.tex.
    """
    
    def __init__(self, adjacency_matrix):
        """
        Initialize the calculator with the adjacency matrix.
        
        Args:
            adjacency_matrix (dict): A dictionary representing the adjacency matrix of the graph.
        """
        self.adjacency_matrix = adjacency_matrix
        
    def calculate_cp_and_scp(self, all_paths):
        """
        Calculate shared points (CP) and sequential shared points (SCP) for all paths.
        
        Implementation based on:
        - Definition 3: CP^i consists of an ordered sequence of points shared with other AGVs
        - Definition 4: SCP^i consists of adjacent points in CP^i
        
        Args:
            all_paths (list): List of paths for all AGVs.
            
        Returns:
            dict: A dictionary containing CP and SCP for each path.
        """
        cp = {}  # Shared points for each AGV path
        scp = {}  # Sequential shared points for each AGV path
        
        # Step 1: Calculate shared points (CP) for each AGV
        # Definition 3: CP^i = {v_x : v_x ∈ Π_i, v_x ∈ Π_j, j ≠ i}
        for i, path_i in enumerate(all_paths):
            if not path_i:
                cp[i] = []
                scp[i] = []
                continue
                
            # Find points that this path shares with any other path
            shared_points = []
            for j, path_j in enumerate(all_paths):
                if i == j or not path_j:  # Skip self-comparison and empty paths
                    continue
                    
                # Find shared points between path_i and path_j
                for point in path_i:
                    if point in path_j and point not in shared_points:
                        shared_points.append(point)
            
            # Sort shared points according to their order in path_i
            cp[i] = sorted(shared_points, key=lambda x: path_i.index(x))
            
        # Step 2: Calculate sequential shared points (SCP) for each AGV
        # Definition 4: SCP^i = {v_p : D(v_p, v_q) ≠ 0, v_p ∈ CP^i, v_q ∈ CP^i}
        for i, shared_points in cp.items():
            scp[i] = []
            
            # Check for sequential (adjacent) shared points
            for p in range(len(shared_points)):
                point_p = shared_points[p]
                
                # Check if this point forms sequential shared points with any other point
                is_sequential = False
                
                for q in range(len(shared_points)):
                    if p == q:  # Skip self
                        continue
                    
                    point_q = shared_points[q]
                    
                    # Check if points are adjacent in the graph (D(v_p, v_q) ≠ 0)
                    if point_q in self.adjacency_matrix.get(point_p, {}):
                        is_sequential = True
                        break
                
                # If this point forms sequential shared points, add it to SCP
                if is_sequential and point_p not in scp[i]:
                    scp[i].append(point_p)
            
        return {"cp": cp, "scp": scp}
