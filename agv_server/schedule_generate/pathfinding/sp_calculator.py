class SpCalculator:
    """Calculates SP (spare points) for sequential shared points."""

    def calculate_sp(self, scp, free_points):
        """
        Calculate spare points (SP) for sequential shared points (SCP).

        Args:
            scp (list): List of sequential shared points.
            free_points (dict): A dictionary of free points for each node.

        Returns:
            dict: A dictionary mapping SCP nodes to their spare points.
        """
        sp = {}
        for point in scp:
            if point in free_points and free_points[point]:
                # Assign the nearest free point
                sp[point] = min(free_points[point],
                                key=lambda x: x["distance"])
            else:
                sp[point] = None  # No spare point available
        return sp