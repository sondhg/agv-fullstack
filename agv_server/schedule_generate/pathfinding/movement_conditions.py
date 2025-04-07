class MovementConditions:
    """Evaluates movement conditions for AGVs."""

    @staticmethod
    def evaluate_condition_1(next_point, scp, reserved_points):
        """
        Evaluate Condition 1: v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}.

        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.

        Returns:
            bool: True if Condition 1 is satisfied, False otherwise.
        """
        return next_point not in scp and next_point not in reserved_points

    @staticmethod
    def evaluate_condition_2(next_point, scp, reserved_points, reserved_by_no_spare):
        """
        Evaluate Condition 2: v_n^i ∈ SCP^i but ∀ v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0}
        and v_n^i ∉ {v_r^j, j ≠ i}.

        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.
            reserved_by_no_spare (set): Points reserved by AGVs without spare points.

        Returns:
            bool: True if Condition 2 is satisfied, False otherwise.
        """
        return (
            next_point in scp
            and all(point not in reserved_by_no_spare for point in scp)
            and next_point not in reserved_points
        )

    @staticmethod
    def evaluate_condition_3(next_point, scp, reserved_points, reserved_by_no_spare, spare_points):
        """
        Evaluate Condition 3: v_n^i ∈ SCP^i and ∃ v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0}
        but SP^i ≠ ∅ and v_n^i ∉ {v_r^j, j ≠ i}.

        Args:
            next_point (int): The next point the AGV wants to move to.
            scp (list): Sequential shared points (SCP^i) of the AGV.
            reserved_points (set): Points reserved by other AGVs.
            reserved_by_no_spare (set): Points reserved by AGVs without spare points.
            spare_points (dict): Spare points (SP^i) of the AGV.

        Returns:
            bool: True if Condition 3 is satisfied, False otherwise.
        """
        return (
            next_point in scp
            and any(point in reserved_by_no_spare for point in scp)
            and spare_points
            and next_point not in reserved_points
        )
