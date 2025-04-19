from rest_framework import serializers
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    assigned_agv = serializers.SerializerMethodField()

    def get_assigned_agv(self, obj):
        if obj.assigned_agv:
            return {
                'agv_id': obj.assigned_agv.agv_id,
            }

    class Meta:
        model = Schedule
        fields = "__all__"
