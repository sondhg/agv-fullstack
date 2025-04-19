from rest_framework import serializers
from .models import Agv


class AGVSerializer(serializers.ModelSerializer):
    # Include complete schedule data
    active_schedule = serializers.SerializerMethodField()

    def get_active_schedule(self, obj):
        if obj.active_schedule:
            return {
                'schedule_id': obj.active_schedule.schedule_id,
                'order_id': obj.active_schedule.order_id,
                'order_date': obj.active_schedule.order_date,
                'start_time': obj.active_schedule.start_time,
                'est_end_time': obj.active_schedule.est_end_time,
                'parking_node': obj.active_schedule.parking_node,
                'storage_node': obj.active_schedule.storage_node,
                'workstation_node': obj.active_schedule.workstation_node,
                'initial_path': obj.active_schedule.initial_path,
                'residual_path': obj.active_schedule.residual_path,
                'cp': obj.active_schedule.cp,
                'scp': obj.active_schedule.scp
            }
        return None

    class Meta:
        model = Agv
        fields = "__all__"
