from django.db import models


class MapData(models.Model):
    node_count = models.IntegerField(default=0)


class Connection(models.Model):
    node1 = models.IntegerField()
    node2 = models.IntegerField()
    distance = models.FloatField()


class Direction(models.Model):
    node1 = models.IntegerField()
    node2 = models.IntegerField()
    direction = models.IntegerField()  # 0-5 values from map-direction.csv
    # node2 is to the {direction} of node1
