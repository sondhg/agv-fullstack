from django.db import models


class Schedule(models.Model):
    schedule_id = models.BigIntegerField(primary_key=True)
    order_id = models.BigIntegerField()
    order_date = models.DateField()
    start_time = models.TimeField()
    est_end_time = models.TimeField(default="00:00:00")  # Default value
    parking_node = models.IntegerField()
    storage_node = models.IntegerField()
    workstation_node = models.IntegerField()
    initial_path = models.TextField(
        # P_i^j: Path of AGV i performing task j from origin parking point through pickup/delivery to final parking point. Once generated, it will not be changed.
        default="[]")
    residual_path = models.TextField(
        # Pi_i: Sequence of remaining points to be visited by AGV i before finishing current task. It will be updated as the AGV moves.
        default="[]")

    # New fields for collision and deadlock avoidance
    cp = models.JSONField(default=list)  # Shared points (CP)
    scp = models.JSONField(default=list)  # Sequential shared points (SCP)
    sp = models.JSONField(default=dict)  # Spare points (SP)
    # Traveling info {v_c, v_n, v_r}
    traveling_info = models.JSONField(default=dict)
    state = models.IntegerField(default=1)  # 0: idle, 1: moving, 2: waiting
    spare_flag = models.BooleanField(default=False)  # F^i: Spare point flag

    def __str__(self):
        return f"Schedule {self.schedule_id} for Order {self.order_id}"

    class Meta:
        ordering = ['schedule_id']  # Ensure ascending order by schedule_id
