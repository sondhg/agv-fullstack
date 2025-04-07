from schedule_generate.models import Schedule


class DeadlockDetector:
    """Detects heading-on and loop deadlocks among AGVs."""

    @staticmethod
    def detect_heading_on_deadlock():
        """
        Detect heading-on deadlocks among AGVs.

        Returns:
            list: A list of tuples representing AGVs involved in heading-on deadlocks.
                  Each tuple contains two schedule IDs (e.g., [(1, 2), (3, 4)]).
        """
        schedules = Schedule.objects.filter(
            state=1)  # Only consider moving AGVs
        deadlocks = []

        for schedule in schedules:
            for other in schedules:
                if (
                    schedule.schedule_id != other.schedule_id  # Different schedules
                    and schedule.traveling_info.get("v_n")  # Ensure v_n exists
                    and schedule.traveling_info.get("v_c")  # Ensure v_c exists
                    # Ensure v_n exists for other
                    and other.traveling_info.get("v_n")
                    # Ensure v_c exists for other
                    and other.traveling_info.get("v_c")
                    # v_n^i = v_c^j
                    and schedule.traveling_info["v_n"] == other.traveling_info["v_c"]
                    # v_n^j = v_c^i
                    and other.traveling_info["v_n"] == schedule.traveling_info["v_c"]
                ):
                    deadlocks.append((schedule.schedule_id, other.schedule_id))

        return deadlocks

    @staticmethod
    def detect_loop_deadlock():
        """
        Detect loop deadlocks among AGVs.

        Returns:
            list: A list of lists representing AGVs involved in loop deadlocks.
                  Each inner list contains schedule IDs forming a loop (e.g., [[1, 2, 3]]).
        """
        schedules = Schedule.objects.filter(
            state=1)  # Only consider moving AGVs
        visited = set()
        loops = []

        def dfs(schedule_id, path):
            if schedule_id in path:
                loop_start = path.index(schedule_id)
                loops.append(path[loop_start:])
                return

            visited.add(schedule_id)
            path.append(schedule_id)

            current_schedule = Schedule.objects.get(schedule_id=schedule_id)
            next_schedule = Schedule.objects.filter(
                traveling_info__v_c=current_schedule.traveling_info["v_n"]
            ).first()

            if next_schedule and next_schedule.schedule_id not in visited:
                dfs(next_schedule.schedule_id, path)

            path.pop()

        for schedule in schedules:
            if schedule.schedule_id not in visited:
                dfs(schedule.schedule_id, [])

        return loops
