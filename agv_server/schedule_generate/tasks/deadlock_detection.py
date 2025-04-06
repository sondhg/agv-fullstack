from schedule_generate.models import Schedule


class DeadlockDetection:
    """Handles deadlock detection and resolution."""

    def detect_and_resolve_deadlocks(self):
        """
        Detect and resolve deadlocks among AGVs.
        """
        schedules = Schedule.objects.all()
        for schedule in schedules:
            if schedule.state == 2:  # Waiting state
                for other in schedules:
                    # Check for heading-on deadlock
                    if (
                        schedule.traveling_info["v_n"] == other.traveling_info["v_c"]
                        and other.traveling_info["v_n"] == schedule.traveling_info["v_c"]
                    ):
                        self.resolve_deadlock(schedule, other)

    def resolve_deadlock(self, schedule, other):
        """
        Resolve a heading-on deadlock between two AGVs.

        Args:
            schedule (Schedule): The first AGV involved in the deadlock.
            other (Schedule): The second AGV involved in the deadlock.
        """
        if schedule.spare_flag:
            schedule.traveling_info["v_n"] = schedule.sp[schedule.traveling_info["v_c"]]
            schedule.save()
        elif other.spare_flag:
            other.traveling_info["v_n"] = other.sp[other.traveling_info["v_c"]]
            other.save()
