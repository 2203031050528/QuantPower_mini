from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class MarketRouter:

    GROUP_NAME = "market_data"

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def route(self, tick):

        async_to_sync(
            self.channel_layer.group_send
        )(
            self.GROUP_NAME,
            {
                "type": "market_tick",
                "data": tick,
            },
        )