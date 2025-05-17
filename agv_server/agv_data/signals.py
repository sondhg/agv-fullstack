# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import Agv
# from .serializers import AGVSerializer


# @receiver(post_save, sender=Agv)
# def agv_post_save(sender, instance, **kwargs):
#     """
#     Signal handler that sends WebSocket messages when AGV instances are saved.
#     This ensures the frontend gets real-time updates whenever AGV data changes.
#     """
#     # Serialize the AGV instance
#     serializer = AGVSerializer(instance)
#     agv_data = serializer.data

#     # Get the channel layer
#     channel_layer = get_channel_layer()

#     # Send message to the WebSocket group
#     async_to_sync(channel_layer.group_send)(
#         "agv_group",
#         {
#             "type": "agv_message",
#             "message": {
#                 "type": "agv_update",
#                 "data": agv_data
#             }
#         }
#     )
