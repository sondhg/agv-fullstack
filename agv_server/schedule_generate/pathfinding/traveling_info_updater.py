class TravelingInfoUpdater:
    """Handles updates to the traveling information of AGVs."""

    @staticmethod
    def update_traveling_info(schedule, current_point, next_point):
        """
        Update the traveling information for a given schedule.

        Args:
            schedule (Schedule): The schedule object to update.
            current_point (int): The current point of the AGV.
            next_point (int): The next point the AGV will visit.

        Returns:
            dict: The updated traveling information.
        """
        traveling_info = schedule.traveling_info or {}

        # Update traveling information
        traveling_info["v_c"] = current_point  # Current point
        traveling_info["v_n"] = next_point  # Next point
        # Reserved point (default to next point)
        traveling_info["v_r"] = next_point

        # Save the updated traveling information to the schedule
        schedule.traveling_info = traveling_info
        schedule.save()

        return traveling_info
