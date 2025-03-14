from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def create(self, request):
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
