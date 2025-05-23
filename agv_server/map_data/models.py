"""Models for storing AGV map data."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .constants import MapConstants


class MapData(models.Model):
    """
    Stores general map information.
    Currently only stores the total number of nodes in the map.
    """
    node_count = models.IntegerField(
        default=MapConstants.DEFAULT_NODE_COUNT,
        validators=[MinValueValidator(0)],
        help_text="Total number of nodes in the map"
    )

    class Meta:
        verbose_name = "Map Data"
        verbose_name_plural = "Map Data"

    def __str__(self):
        return f"Map with {self.node_count} nodes"


class Connection(models.Model):
    """
    Represents a connection between two nodes in the map.
    Stores the distance between connected nodes.
    A value of 10000 in the CSV indicates no connection.
    """
    node1 = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Starting node of the connection"
    )
    node2 = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Ending node of the connection"
    )
    distance = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Distance between the nodes"
    )

    class Meta:
        verbose_name = "Connection"
        verbose_name_plural = "Connections"
        unique_together = ['node1', 'node2']
        indexes = [
            models.Index(fields=['node1']),
            models.Index(fields=['node2']),
        ]

    def __str__(self):
        return f"{self.node1} connects to {self.node2} (distance: {self.distance})"


class Direction(models.Model):
    """
    Represents the directional relationship between two nodes.
    The direction value indicates the cardinal direction from node1 to node2:
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4
    A value of 10000 in the CSV indicates no direction (no connection).
    """

    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    DIRECTION_CHOICES = {
        NORTH: 'North',
        EAST: 'East',
        SOUTH: 'South',
        WEST: 'West',
    }

    node1 = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Reference node (starting point)"
    )
    node2 = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Target node (ending point)"
    )
    direction = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ],
        choices=DIRECTION_CHOICES,
        help_text="Cardinal direction from node1 to node2 (1=North, 2=East, 3=South, 4=West)"
    )

    class Meta:
        verbose_name = "Direction"
        verbose_name_plural = "Directions"
        unique_together = ['node1', 'node2']
        indexes = [
            models.Index(fields=['node1']),
            models.Index(fields=['node2']),
        ]

    def __str__(self):
        direction_name = dict(self.DIRECTION_CHOICES)[
            self.direction]
        return f"Node {self.node2} is {direction_name} of node {self.node1}"
