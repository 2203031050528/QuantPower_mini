from dhan.models import DhanAccount
import requests


class DhanAdapter:

    BASE_URL = "https://api.dhan.co"

    def __init__(self, user):

        self.user = user

        try:
            self.account = DhanAccount.objects.get(
                user=user,
                is_active=True,
            )
        except DhanAccount.DoesNotExist:
            raise ValueError(
                "Active Dhan account not connected"
            )

        self.access_token = self.account.access_token

    @property
    def headers(self):
        return {
            "access-token": self.access_token,
            "Content-Type": "application/json",
        }

    def build_order_payload(
        self,
        security_id,
        quantity,
        side,
        order_type="MARKET",
        product_type="INTRADAY",
        exchange_segment="NSE_FNO",
        price=0,
    ):

        return {
            "dhanClientId": self.account.client_id,
            "transactionType": side,
            "exchangeSegment": exchange_segment,
            "productType": product_type,
            "orderType": order_type,
            "securityId": security_id,
            "quantity": quantity,
            "price": price,
        }

    def send_order(self, payload):

        response = requests.post(
            f"{self.BASE_URL}/orders",
            headers=self.headers,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()