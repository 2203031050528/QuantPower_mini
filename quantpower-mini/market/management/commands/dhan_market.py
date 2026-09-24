from django.core.management.base import (
    BaseCommand,
)

from market.dhan_feed import (
    DhanMarketFeed,
)


class Command(BaseCommand):

    help = "Start Dhan live market feed"

    def handle(
        self,
        *args,
        **options,
    ):

        instruments = [
            {
                "ExchangeSegment": "NSE_EQ",
                "SecurityId": "1333",
            }
        ]

        feed = DhanMarketFeed(
            instruments
        )

        feed.run()
