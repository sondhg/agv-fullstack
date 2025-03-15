from django.urls import path
from .views import import_connections, import_directions, get_map_data

urlpatterns = [
    path("import-connections/", import_connections, name="import-connections"),
    path("import-directions/", import_directions, name="import-directions"),
    path("get-map-data/", get_map_data, name="get-map-data"),
]
