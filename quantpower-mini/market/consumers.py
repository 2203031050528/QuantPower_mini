import json

from channels.generic.websocket import (
    AsyncWebsocketConsumer,
)


class MarketConsumer(
    AsyncWebsocketConsumer
):

    GROUP_NAME = "market_data"

    async def connect(self):

        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name,
        )

        await self.accept()

        await self.send(
            text_data=json.dumps({
                "type": "connection",
                "message": (
                    "Market WebSocket connected"
                ),
            })
        )

    async def disconnect(
        self,
        close_code,
    ):

        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name,
        )

    async def market_tick(
        self,
        event,
    ):

        await self.send(
            text_data=json.dumps(
                event["data"]
            )
        )