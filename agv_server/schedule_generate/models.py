from django.db import models


class Schedule(models.Model):
    schedule_id = models.BigIntegerField(primary_key=True)
    order_id = models.BigIntegerField()
    order_date = models.DateField()
    start_time = models.TimeField()
    est_end_time = models.TimeField(default="00:00:00")  # Default value
    start_point = models.IntegerField()
    end_point = models.IntegerField()
    load_name = models.CharField(max_length=100)
    load_amount = models.IntegerField(default=0)
    load_weight = models.IntegerField(default=0)
    instruction_set = models.TextField(
        default="[]")  # Default value as JSON string

    def __str__(self):
        return f"Schedule {self.schedule_id} for Order {self.order_id}"

    class Meta:
        ordering = ['schedule_id']  # Ensure ascending order by schedule_id
