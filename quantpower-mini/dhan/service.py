import requests
from django.conf import settings


class DhanClient:

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
        url = f"{self.BASE_URL}{endpoint}"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()