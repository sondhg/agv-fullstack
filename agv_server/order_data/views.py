from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from rest_framework.generics import ListAPIView


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
        try:
            order = Order.objects.get(order_id=order_id)
            order.delete()
            return Response(
                {"message": f"Order {order_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": f"Schedule {order_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BulkDeleteOrdersView(APIView):
    def delete(self, request):
        try:
            order_ids = request.data.get("order_ids", [])
            if not order_ids:
                return Response(
                    {"error": "No order IDs provided for deletion."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
