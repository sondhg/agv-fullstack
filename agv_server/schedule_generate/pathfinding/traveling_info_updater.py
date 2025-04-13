class TravelingInfoUpdater:
    """Updates traveling info for AGVs based on their current and next positions."""

    @staticmethod
    def update_traveling_info(current_point: int, next_point: int, residual_path: list) -> tuple:
        """
        Update the traveling info and residual path for an AGV.
        
        Args:
            current_point (int): The current point of the AGV
            next_point (int): The next point the AGV wants to move to
            residual_path (list): The current residual path
            
        Returns:
            tuple: (new_traveling_info, new_residual_path)
        """
        # Create new traveling info
        new_traveling_info = {
            "v_c": current_point,
            "v_n": next_point,
            "v_r": next_point  # Initially set v_r = v_n, may be updated later
        }
        
        # Update residual path - remove all points up to and including current_point
        try:
            current_idx = residual_path.index(current_point)
            new_residual_path = residual_path[current_idx + 1:]
        except ValueError:
            # If current_point not found in path, keep existing path
            new_residual_path = residual_path
            
        return new_traveling_info, new_residual_path
