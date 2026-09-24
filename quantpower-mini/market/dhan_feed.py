import json
import time

import websocket

from django.conf import settings

from market.dhan_parser import DhanPacketParser
from market.feed_manager import MarketFeedManager


class DhanMarketFeed:

    WS_URL = (
        "wss://api-feed.dhan.co"
        "?version=2"
        "&token={token}"
        "&clientId={client_id}"
        "&authType=2"
    )

    def __init__(self, instruments):

        self.client_id = settings.DHAN_CLIENT_ID

        self.access_token = (
            settings.DHAN_ACCESS_TOKEN
        )

        self.instruments = instruments

        self.manager = MarketFeedManager()

        self.ws = None

    def build_url(self):

        return self.WS_URL.format(
            token=self.access_token,
            client_id=self.client_id,
        )

    def subscribe(self):

        payload = {
            "RequestCode": 15,
            "InstrumentCount": len(
                self.instruments
            ),
            "InstrumentList": self.instruments,
        }

        self.ws.send(
            json.dumps(payload)
        )

    def on_open(self, ws):

        print(
            "Dhan market feed connected"
        )

        self.ws = ws

        self.subscribe()

    def on_message(self, ws, message):

        if isinstance(message, str):

            print(
                "Dhan text message:",
                message,
            )

            return

        tick = DhanPacketParser.parse(
            message
        )

        if not tick:
            return

        if tick["type"] == "ticker":

            self.manager.process_tick(
                tick
            )

            print(
                tick
            )

        elif tick["type"] == "disconnect":

            print(
                "Dhan feed disconnected:",
                tick["reason"],
            )

    def on_error(self, ws, error):

        print(
            "Dhan WebSocket error:",
            error,
        )

    def on_close(
        self,
        ws,
        close_status_code,
        close_msg,
    ):

        print(
            "Dhan WebSocket closed:",
            close_status_code,
            close_msg,
        )

    def run(self):

        if not self.client_id:
            raise ValueError(
                "DHAN_CLIENT_ID is missing"
            )

        if not self.access_token:
            raise ValueError(
                "DHAN_ACCESS_TOKEN is missing"
            )

        while True:

            try:

                ws = websocket.WebSocketApp(
                    self.build_url(),
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                )

                ws.run_forever(
                    ping_interval=20,
                    ping_timeout=10,
                )

            except Exception as exc:

                print(
                    "Feed exception:",
                    exc,
                )

            print(
                "Reconnecting in 5 seconds..."
            )

            time.sleep(5)
