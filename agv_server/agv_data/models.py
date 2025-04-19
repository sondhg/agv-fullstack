from django.db import models
from schedule_generate.models import Schedule

# AGV States from Algorithm 2 (SA^i)
AGV_STATE_IDLE = 0    # No mission to execute
AGV_STATE_MOVING = 1  # On way to next reserved point 
AGV_STATE_WAITING = 2  # Stopped at current point

class Agv(models.Model):
    """
    Represents an AGV in the system according to the DSPA algorithm.
    Following Algorithm 2's control policy and Algorithm 3's deadlock resolution.
    """
    # Basic AGV information
    agv_id = models.BigIntegerField(primary_key=True)
    preferred_parking_node = models.IntegerField(
        help_text="Preferred parking point for AGV"
    )

    # Traveling information I^i from Definition 8
    current_node = models.IntegerField(
        null=True, 
        help_text="Current position (v_c^i): point where AGV is located or last left"
    )
    next_node = models.IntegerField(
        null=True, 
        help_text="Next point to visit (v_n^i)"
    )
    reserved_node = models.IntegerField(
        null=True, 
        help_text="Reserved point (v_r^i)"
    )

    # State management from Algorithm 2
    motion_state = models.IntegerField(
        choices=[
            (AGV_STATE_IDLE, 'Idle'),
            (AGV_STATE_MOVING, 'Moving'),
            (AGV_STATE_WAITING, 'Waiting')
        ],
        default=AGV_STATE_IDLE,
        help_text="AGV state (SA^i) as defined in Definition 7"
    )

    # DSPA algorithm specific fields from Algorithm 2
    spare_flag = models.BooleanField(
        default=False,
        help_text="F^i: indicates if AGV moves along shared points with sufficient spare points"
    )
    spare_points = models.JSONField(
        default=dict,
        help_text="SP^i: mapping of shared points to their allocated spare points"
    )

    # Current schedule
    active_schedule = models.OneToOneField(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_agv',
        help_text="Currently executing schedule"
    )

    def save(self, *args, **kwargs):
        # Initialize current_node to preferred_parking_node for new AGVs
        if not self.pk and self.current_node is None:
            self.current_node = self.preferred_parking_node
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "AGV"
        verbose_name_plural = "AGVs"
        ordering = ['agv_id']

    def __str__(self):
        return f"AGV {self.agv_id}"
