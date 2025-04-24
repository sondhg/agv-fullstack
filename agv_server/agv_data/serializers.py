from rest_framework import serializers
from .models import Agv
from order_data.models import Order


class OrderInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for basic order information needed in AGV responses.
    """
    class Meta:
        model = Order
        fields = ('order_id', 'order_date', 'start_time',
                  'parking_node', 'storage_node', 'workstation_node')


class AGVSerializer(serializers.ModelSerializer):
    """
    Serializer for the AGV model that includes active order information.
    This replaces the previous implementation that included schedule data.
    """
    # Include order information for API compatibility
    active_order_info = serializers.SerializerMethodField()

    # For backwards compatibility with frontend code
    active_schedule = serializers.SerializerMethodField()

    def get_active_order_info(self, obj):
        """
        Get detailed information about the AGV's active order.

        Args:
            obj: The AGV instance being serialized

        Returns:
            dict: Order information or None if no active order
        """
        if obj.active_order:
            return OrderInfoSerializer(obj.active_order).data
        return None

    def get_active_schedule(self, obj):
        """
        Maintain backwards compatibility with frontend code that expects
        schedule information. This maps order and path data from the AGV
        to the previous schedule format.

        Args:
            obj: The AGV instance being serialized

        Returns:
            dict: Schedule-formatted information or None if no active order
        """
        if obj.active_order:
            # Map AGV and Order data to the expected schedule format
            return {
                'schedule_id': obj.active_order.order_id,  # Using order_id as schedule_id
                'order_id': obj.active_order.order_id,
                'order_date': obj.active_order.order_date,
                'start_time': obj.active_order.start_time,
                'parking_node': obj.active_order.parking_node,
                'storage_node': obj.active_order.storage_node,
                'workstation_node': obj.active_order.workstation_node,
                'initial_path': obj.initial_path,
                'residual_path': obj.residual_path,
                'cp': obj.cp,
                'scp': obj.scp
            }
        return None

    class Meta:
        model = Agv
        fields = "__all__"
