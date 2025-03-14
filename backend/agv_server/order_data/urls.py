from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderView

router = DefaultRouter()
# localhost:8000/api/orders/
router.register(r'orders', OrderView, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
