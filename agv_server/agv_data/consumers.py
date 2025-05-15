from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.decorators import action

from .serializers import AGVSerializer
from .models import Agv


class AgvConsumer(GenericAsyncAPIConsumer):
    queryset = Agv.objects.all()
    serializer_class = AGVSerializer

    @model_observer(Agv)
    async def agv_activity(self, message: AGVSerializer, observer=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.send_json({"message": message, "request_id": request_id})

    @agv_activity.serializer
    def agv_activity(self, instance: Agv, action, **kwargs) -> AGVSerializer:
        """
        This will return the AGV serializer.
        """
        return AGVSerializer(instance).data

    @action()
    async def subscribe_to_agv_activity(self, request_id, **kwargs):
        await self.agv_activity.subscribe(request_id=request_id)
