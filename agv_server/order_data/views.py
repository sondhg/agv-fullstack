from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from rest_framework.generics import ListAPIView
from agv_data.models import Agv
from agv_data.constants import AGVState
from django.db import transaction


class ListOrdersView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CreateOrderView(APIView):
    def post(self, request):
        if isinstance(request.data, list):
            # Handle multiple objects
            serializer = OrderSerializer(data=request.data, many=True)
        else:
            # Handle single object
            serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteOrderView(APIView):
    def delete(self, request, order_id):
        """
        Delete an order by its ID and reset the associated AGV if it exists.

        Args:
            request: The HTTP request
            order_id: The ID of the order to delete

        Returns:
            Response: A response indicating success or failure
        """
        try:
            # Use a transaction to ensure both order deletion and AGV reset are atomic
            with transaction.atomic():
                order = Order.objects.get(order_id=order_id)

                # Check if there's an AGV associated with this order
                try:
                    # Get the AGV directly with a query instead of through relationship
                    # This ensures we're getting the most up-to-date data
                    associated_agv = Agv.objects.filter(
                        active_order_id=order_id).first()
                    if associated_agv:
                        # Reset AGV fields to default values
                        self._reset_agv(associated_agv)

                except Exception as agv_error:
                    # Log the error but continue with order deletion
                    print(
                        f"Error resetting AGV for order {order_id}: {str(agv_error)}")

                # Delete the order
                order.delete()

            return Response(
                {"message": f"Order {order_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": f"Order {order_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @transaction.atomic
    def _reset_agv(self, agv):
        """
        Reset AGV fields to their default values.

        Args:
            agv: The AGV object to reset
        """
        # Reset only necessary fields, keeping agv_id and preferred_parking_node
        agv.current_node = None
        agv.next_node = None
        agv.reserved_node = None
        agv.motion_state = AGVState.IDLE
        agv.spare_flag = False
        agv.spare_points = {}
        agv.initial_path = []
        agv.residual_path = []
        agv.cp = []
        agv.scp = []
        agv.active_order = None

        # Ensure changes are saved and committed
        agv.save(update_fields=[
            'current_node', 'next_node', 'reserved_node', 'motion_state',
            'spare_flag', 'spare_points', 'initial_path', 'residual_path',
            'cp', 'scp', 'active_order'
        ])

        # Verify that the AGV was reset properly
        refreshed_agv = Agv.objects.get(pk=agv.pk)
        if refreshed_agv.current_node is not None:
            print(
                f"Warning: AGV {agv.agv_id} current_node was not reset properly")


class BulkDeleteOrdersView(APIView):
    def delete(self, request):
        """
        Delete multiple orders by their IDs and reset associated AGVs.

        Args:
            request: The HTTP request containing order_ids to delete

        Returns:
            Response: A response indicating success or failure
        """
        try:
            order_ids = request.data.get("order_ids", [])
            if not order_ids:
                return Response(
                    {"error": "No order IDs provided for deletion."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use a transaction for the entire operation
            with transaction.atomic():
                # First, reset any AGVs associated with these orders
                self._reset_associated_agvs(order_ids)

                # Then delete the orders
                deleted_count, _ = Order.objects.filter(
                    order_id__in=order_ids).delete()

            return Response(
                {"message": f"{deleted_count} orders deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during bulk deletion: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def _reset_associated_agvs(self, order_ids):
        """
        Reset all AGVs associated with the given order IDs.

        Args:
            order_ids: List of order IDs to check for associated AGVs
        """
        # Find AGVs with active_order in the list of order_ids
        # Using select_for_update to lock the rows during update
        agvs_to_reset = Agv.objects.filter(
            active_order__order_id__in=order_ids).select_for_update()

        reset_agvs_ids = []
        for agv in agvs_to_reset:
            # Store AGV ID for verification later
            reset_agvs_ids.append(agv.agv_id)

            # Reset AGV fields to default values
            agv.current_node = None
            agv.next_node = None
            agv.reserved_node = None
            agv.motion_state = AGVState.IDLE
            agv.spare_flag = False
            agv.spare_points = {}
            agv.initial_path = []
            agv.residual_path = []
            agv.cp = []
            agv.scp = []
            agv.active_order = None

            # Save with specific fields to update
            agv.save(update_fields=[
                'current_node', 'next_node', 'reserved_node', 'motion_state',
                'spare_flag', 'spare_points', 'initial_path', 'residual_path',
                'cp', 'scp', 'active_order'
            ])

        # Verify all AGVs were properly reset
        if reset_agvs_ids:
            # Re-query to make sure changes were committed
            still_active_agvs = Agv.objects.filter(
                agv_id__in=reset_agvs_ids,
                current_node__isnull=False
            ).values_list('agv_id', flat=True)

            if still_active_agvs:
                print(
                    f"Warning: The following AGVs weren't reset properly: {list(still_active_agvs)}")
                # Force another save attempt on these AGVs
                for agv_id in still_active_agvs:
                    try:
                        agv = Agv.objects.get(agv_id=agv_id)
                        agv.current_node = None
                        agv.save(update_fields=['current_node'])
                    except Exception as e:
                        print(
                            f"Error during second reset attempt for AGV {agv_id}: {str(e)}")
