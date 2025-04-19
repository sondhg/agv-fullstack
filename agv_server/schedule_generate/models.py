from django.db import models


class Schedule(models.Model):
    """
    Represents a task schedule in the system according to DSPA algorithm.
    Stores path information and task details.
    """
    schedule_id = models.BigIntegerField(primary_key=True)
    order_id = models.BigIntegerField()
    order_date = models.DateField()
    start_time = models.TimeField()
    est_end_time = models.TimeField(default="00:00:00")
    
    # Task nodes
    parking_node = models.IntegerField()
    storage_node = models.IntegerField()
    workstation_node = models.IntegerField()
    
    # AGV assignment
    assigned_agv = models.ForeignKey('agv_data.Agv', on_delete=models.SET_NULL, null=True, blank=True)
    
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

    def __str__(self):
        return f"Schedule {self.schedule_id} for Order {self.order_id}"

    class Meta:
        ordering = ['schedule_id']
