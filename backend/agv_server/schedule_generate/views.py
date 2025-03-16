from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule
from .serializers import ScheduleSerializer
from order_data.models import Order
from order_data.serializers import OrderSerializer
from rest_framework.generics import ListAPIView


class GenerateSchedulesView(APIView):
    def post(self, request):
        try:
            # Fetch all orders
            orders = Order.objects.all()
            if not orders.exists():
                return Response(
                    {"message": "No orders available to generate schedules."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            schedules = []
            for order in orders:
                # Check if a schedule for this order already exists
                if Schedule.objects.filter(schedule_id=order.order_id).exists():
                    return Response(
                        {"warning": f"A schedule with order_id {order.order_id} already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Create a schedule based on the order
                schedule_data = {
                    "schedule_id": order.order_id,
                    "order_id": order.order_id,
                    "order_date": order.order_date,
                    "start_time": order.start_time,
                    "start_point": order.start_point,
                    "end_point": order.end_point,
                    "load_name": order.load_name,
                    "load_amount": order.load_amount,
                    "load_weight": order.load_weight,
                    "est_end_time": "00:00:00",  # Default value
                    "instruction_set": "[]",    # Default value
                }
                serializer = ScheduleSerializer(data=schedule_data)
                if serializer.is_valid():
                    serializer.save()
                    schedules.append(serializer.data)

                    # Delete the corresponding order after creating the schedule
                    order.delete()

            return Response(
                {"message": "Schedules generated successfully.",
                    "schedules": schedules},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListSchedulesView(ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class DeleteScheduleView(APIView):
    def delete(self, request, schedule_id):
        try:
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            schedule.delete()
            return Response(
                {"message": f"Schedule {schedule_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Schedule.DoesNotExist:
            return Response(
                {"error": f"Schedule {schedule_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
