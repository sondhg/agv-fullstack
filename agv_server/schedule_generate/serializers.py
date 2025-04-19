from rest_framework import serializers
from .models import Schedule
from agv_data.serializers import AGVSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    assigned_agv = AGVSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
