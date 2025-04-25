from django.db import models
from order_data.models import Order


class Agv(models.Model):
    """
    Represents an AGV in the system according to the DSPA algorithm.
    Following Algorithm 2's control policy and Algorithm 3's deadlock resolution.
    """

    # Define choices for motion_state
    # Actual integer values to be set on model
    IDLE = 0  # No mission to execute
    MOVING = 1  # On way to next reserved point
    WAITING = 2  # Stopped at current point

    # Human readable names
    MOTION_STATE_CHOICES = {
        IDLE: "Idle",
        MOVING: "Moving",
        WAITING: "Waiting"
    }

    # Define choices for direction_change
    # Actual integer values to be set on model
    GO_STRAIGHT = 0  # Go straight
    TURN_AROUND = 1  # Reverse
    TURN_LEFT = 2  # Turn left
    TURN_RIGHT = 3  # Turn right

    # Human readable names
    DIRECTION_CHANGE_CHOICES = {
        GO_STRAIGHT: "Go straight",
        TURN_AROUND: "Turn around",
        TURN_LEFT: "Turn left",
        TURN_RIGHT: "Turn right"
    }

    # Model fields
    # Basic AGV information
    agv_id = models.BigIntegerField(primary_key=True)
    preferred_parking_node = models.IntegerField(
        help_text="Preferred parking point for AGV"
    )

    direction_change = models.IntegerField(
        choices=DIRECTION_CHANGE_CHOICES,
        null=True,
        help_text="Direction the AGV should turn to after reaching a node",
    )

    # previous_node is not needed for DSPA, but will be useful for deciding which direction to turn to when AGV reaches a node, based on considering the relevant three consecutive nodes and the map layout.
    previous_node = models.IntegerField(
        null=True,
        help_text="Last point visited"
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
        choices=MOTION_STATE_CHOICES,
        default=IDLE,
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

    # Path information according to Algorithm 1
    initial_path = models.JSONField(
        help_text="P_i^j: Path of AGV i performing task j. Once generated, will not change.",
        default=list
    )
    residual_path = models.JSONField(
        help_text="Pi_i: Remaining points to be visited by AGV i.",
        default=list
    )
    cp = models.JSONField(
        help_text="CP: Shared points with other AGVs",
        default=list
    )
    scp = models.JSONField(
        help_text="SCP: Sequential shared points",
        default=list
    )

    # Current order
    active_order = models.OneToOneField(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_agv',
        help_text="Currently executing order"
    )

    class Meta:
        verbose_name = "AGV"
        verbose_name_plural = "AGVs"
        ordering = ['agv_id']

    def __str__(self):
        return f"AGV {self.agv_id}"
