import random
import time

from django.core.management.base import BaseCommand

from market.redis_service import save_tick
from market.router import MarketRouter


class Command(BaseCommand):

    help = "Generate mock market ticks"

    def handle(self, *args, **options):

        router = MarketRouter()

        price = 25250.0

        self.stdout.write(
            self.style.SUCCESS(
                "Mock market started..."
            )
        )

        while True:

            price += random.uniform(
                -5,
                5,
            )

            tick = {
                "symbol": "NIFTY",
                "security_id": "12345",
                "ltp": round(price, 2),
                "timestamp": time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

            # 1. Store latest tick in Redis
            save_tick(
                "12345",
                tick,
            )

            # 2. Send tick to WebSocket users
            router.route(tick)

            self.stdout.write(
                f"NIFTY: {tick['ltp']}"
            )

            time.sleep(1)