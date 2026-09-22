import requests


class DhanMarketDataClient:

    BASE_URL = "https://api.dhan.co"

    def __init__(self, access_token):
        self.access_token = access_token

    @property
    def headers(self):
        return {
            "access-token": self.access_token,
            "Content-Type": "application/json",
        }

    def get(self, endpoint):
        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()