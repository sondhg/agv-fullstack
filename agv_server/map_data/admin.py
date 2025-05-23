from django.contrib import admin
from .models import MapData, Connection, Direction

# Register your models here.
admin.site.register(MapData)
admin.site.register(Connection)
admin.site.register(Direction)
