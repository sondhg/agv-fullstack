from django.urls import path
from .views import import_connections, import_directions, get_map_data, delete_all_map_data

urlpatterns = [
    path("import-connections/", import_connections, name="import-connections"),
    path("import-directions/", import_directions, name="import-directions"),
    path("get/", get_map_data, name="get-map-data"),
    path("delete/", delete_all_map_data, name="delete-all-map-data"),
]
