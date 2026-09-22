import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class MarketRouter:

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def route(self, tick):

        async_to_sync(
            self.channel_layer.group_send
        )(
            "market_data",
            {
                "type": "market_tick",
                "data": tick,
            },
        )