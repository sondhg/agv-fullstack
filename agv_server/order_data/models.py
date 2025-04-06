from django.db import models

from users.models import User


class Order(models.Model):
    order_id = models.BigIntegerField(primary_key=True)
    order_date = models.DateField()
    start_time = models.TimeField()
    parking_node = models.IntegerField()
    storage_node = models.IntegerField()
    workstation_node = models.IntegerField()

    def __str__(self):
        return f"Order {self.order_id} has been created"

    class Meta:
        ordering = ['order_id']  # Ensure ascending order by order_id
