class MovementConditions:
    """
    Evaluates movement conditions for AGVs.
    Implementation based on Algorithm 2 from the algorithms-pseudocode.tex.
    
    Implements the three conditions from Algorithm 2 in the paper:
    
    Condition 1: v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
    Condition 2: v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} and v_n^i ∉ {v_r^j, j ≠ i}
    Condition 3: v_n^i ∈ SCP^i and ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0} but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}
    """

    @staticmethod
    def evaluate_condition_1(next_point, scp, reserved_points):
        """
        Evaluate Condition 1: v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}.
        
        This condition checks if:
        1. The next point is not in the sequential shared points
        2. The next point is not reserved by another AGV
        
        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.
            
        Returns:
            bool: True if Condition 1 is satisfied, False otherwise.
        """
        # The next point should not be in the sequential shared points set
        not_in_scp = next_point not in scp
        
        # The next point should not be reserved by any other AGV
        not_reserved = next_point not in reserved_points
        
        return not_in_scp and not_reserved

    @staticmethod
    def evaluate_condition_2(next_point, scp, reserved_points, reserved_by_no_spare):
        """
        Evaluate Condition 2: v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0}
        and v_n^i ∉ {v_r^j, j ≠ i}.
        
        This condition checks if:
        1. The next point is in the sequential shared points
        2. NO point in the sequential shared points is reserved by an AGV without spare points
        3. The next point is not reserved by another AGV
        
        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.
            reserved_by_no_spare (set): Points reserved by AGVs without spare points.
            
        Returns:
            bool: True if Condition 2 is satisfied, False otherwise.
        """
        # The next point should be in the sequential shared points set
        in_scp = next_point in scp
        
        # ALL points in SCP should NOT be reserved by AGVs without spare points
        no_scp_points_reserved_by_no_spare = all(point not in reserved_by_no_spare for point in scp)
        
        # The next point should not be reserved by any other AGV
        not_reserved = next_point not in reserved_points
        
        return in_scp and no_scp_points_reserved_by_no_spare and not_reserved

    @staticmethod
    def evaluate_condition_3(next_point, scp, reserved_points, reserved_by_no_spare, spare_points):
        """
        Evaluate Condition 3: v_n^i ∈ SCP^i and ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0}
        but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}.
        
        This condition checks if:
        1. The next point is in the sequential shared points
        2. SOME point in the sequential shared points IS reserved by an AGV without spare points
        3. The AGV has spare points allocated (SP^i ≠ ∅)
        4. The next point is not reserved by another AGV
        
        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.
            reserved_by_no_spare (set): Points reserved by AGVs without spare points.
            spare_points (dict): Spare points (SP^i) of the AGV.
            
        Returns:
            bool: True if Condition 3 is satisfied, False otherwise.
        """
        # The next point should be in the sequential shared points set
        in_scp = next_point in scp
        
        # Some point in SCP should be reserved by an AGV without spare points
        some_scp_point_reserved_by_no_spare = any(point in reserved_by_no_spare for point in scp)
        
        # The AGV should have spare points allocated
        has_spare_points = bool(spare_points)
        
        # The next point should not be reserved by any other AGV
        not_reserved = next_point not in reserved_points
        
        return in_scp and some_scp_point_reserved_by_no_spare and has_spare_points and not_reserved
        
    @staticmethod
    def should_update_spare_flag(current_point, next_point, scp, spare_flag, spare_points):
        """
        Determine if the spare_flag (F^i) should be updated.
        
        According to Algorithm 2, F^i should be:
        - Set to 0 and SP^i emptied when leaving sequential shared points (SCP^i)
        - Set to 1 when entering sequential shared points with valid spare points
        
        Args:
            current_point (int): The current point of the AGV (v_c^i).
            next_point (int): The next point the AGV wants to move to (v_n^i).
            scp (list): Sequential shared points (SCP^i) of the AGV.
            spare_flag (bool): Current value of spare_flag (F^i).
            spare_points (dict): Spare points (SP^i) of the AGV.
            
        Returns:
            tuple: (new_spare_flag, should_clear_sp) 
                  new_spare_flag is the updated value of F^i
                  should_clear_sp indicates if SP^i should be emptied
        """
        # When leaving sequential shared points, set F^i = 0 and clear SP^i
        if current_point in scp and next_point not in scp:
            return False, True  # F^i = 0, clear SP^i
            
        # When entering sequential shared points with valid spare points, set F^i = 1
        if current_point not in scp and next_point in scp and spare_points:
            return True, False  # F^i = 1, keep SP^i
            
        # No change in spare_flag and SP^i
        return spare_flag, False
        
    @staticmethod
    def should_remove_current_spare_point(current_point, spare_flag, spare_points):
        """
        Determine if the spare point for the current position should be removed.
        
        According to Algorithm 2 lines 14-16, when an AGV is traveling in sequential 
        shared points with spare points (F^i = 1), it should remove the spare point
        for its current position when it reaches a new point.
        
        Args:
            current_point (int): The current point of the AGV (v_c^i).
            spare_flag (bool): Value of spare_flag (F^i).
            spare_points (dict): Spare points (SP^i) of the AGV.
            
        Returns:
            bool: True if the spare point for current_point should be removed, False otherwise.
        """
        # Convert current_point to string since spare points keys are stored as strings
        current_point_str = str(current_point)
        
        # Should remove the spare point if:
        # 1. AGV has spare points (F^i = 1)
        # 2. The current point has an assigned spare point
        return spare_flag and current_point_str in spare_points
