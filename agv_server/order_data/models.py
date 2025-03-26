from django.db import models

from users.models import User


class Order(models.Model):
    order_id = models.BigIntegerField(primary_key=True)
    order_date = models.DateField()
    start_time = models.TimeField()
    start_point = models.IntegerField()
    end_point = models.IntegerField()
    load_name = models.CharField(max_length=100)
    load_amount = models.IntegerField(default=0)
    load_weight = models.IntegerField(default=0)
    user_name = models.ForeignKey(
        User, to_field='name', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Order {self.order_id} has been created"

    class Meta:
        ordering = ['order_id']  # Ensure ascending order by order_id
