from rest_framework import serializers
from .models import Agv


class AGVSerializer(serializers.ModelSerializer):
    # Extract active_schedule ID if it exists
    active_schedule = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Agv
        fields = "__all__"
