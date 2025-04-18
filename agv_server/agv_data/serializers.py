from rest_framework import serializers
from .models import Agv

class AGVSerializer(serializers.ModelSerializer):
    # Extract active_schedule ID if it exists
    active_schedule = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Agv
        fields = [
            'agv_id',
            'preferred_parking_node',
            'current_node',
            'next_node',
            'reserved_node',
            'motion_state',
            'spare_flag',
            'in_sequential_shared_points',
            'is_deadlocked',
            'last_spare_point',
            'active_schedule',
        ]