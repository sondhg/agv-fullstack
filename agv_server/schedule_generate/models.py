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
    instruction_set = models.TextField(
        default="[]")  # Default value as JSON string

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
