from channels.generic.websocket import AsyncWebsocketConsumer
import json


class AgvConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        print("WebSocket connection established")
        self.room_group_name = "agv_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection
        print(f"WebSocket connection closed with code: {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def agv_message(self, event):
        # Send AGV update message to WebSocket client
        message = event['message']

        # Forward the message to the WebSocket client
        await self.send(text_data=json.dumps(message))
