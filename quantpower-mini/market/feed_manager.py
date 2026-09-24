from market.redis_service import (
    save_tick,
    publish_tick,
)

from market.router import MarketRouter


class MarketFeedManager:

    def __init__(self):
        self.router = MarketRouter()

    def process_tick(
        self,
        tick,
    ):

        security_id = (
            tick["security_id"]
        )

        save_tick(
            security_id,
            tick,
        )

        publish_tick(
            tick
        )

        self.router.route(
            tick
        )
