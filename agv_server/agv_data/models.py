from django.db import models
from schedule_generate.models import Schedule
# AGV States from the paper (SA^i)
AGV_STATE_IDLE = 0    # No mission to execute
AGV_STATE_MOVING = 1  # On way to next reserved point
AGV_STATE_WAITING = 2  # Stopped at current point


class Agv(models.Model):
    """
    Represents an AGV in the system according to the DSPA algorithm.
    Stores both physical state and algorithm-specific data.
    """
    # Basic AGV information
    agv_id = models.BigIntegerField(primary_key=True)

    # Current physical state
    current_node = models.IntegerField(help_text="Current position (v_c^i)")
    next_node = models.IntegerField(
        null=True, help_text="Next point to visit (v_n^i)")
    reserved_node = models.IntegerField(
        null=True, help_text="Reserved point (v_r^i)")

    # Algorithm states
    motion_state = models.IntegerField(
        choices=[
            (AGV_STATE_IDLE, 'Idle'),
            (AGV_STATE_MOVING, 'Moving'),
            (AGV_STATE_WAITING, 'Waiting')
        ],
        default=AGV_STATE_IDLE,
        help_text="AGV state (SA^i)"
    )

    # DSPA algorithm specific fields
    spare_flag = models.BooleanField(
        default=False,
        help_text="Indicates if AGV has spare points (F^i)"
    )

    # Current task information
    active_schedule = models.OneToOneField(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_agv',
        help_text="Current active schedule being executed"
    )

    in_sequential_shared_points = models.BooleanField(
        default=False,
        help_text="Indicates if AGV is currently in sequential shared points"
    )

    is_deadlocked = models.BooleanField(
        default=False,
        help_text="Indicates if AGV is currently in a deadlock situation"
    )

    last_spare_point = models.IntegerField(
        null=True,
        blank=True,
        help_text="Last spare point used to resolve deadlock"
    )

    class Meta:
        verbose_name = "AGV"
        verbose_name_plural = "AGVs"

    def __str__(self):
        return f"AGV {self.agv_id}"
