from django.contrib.auth import base_user
from decimal import Decimal
from proxy.services import ProxyService
from django.db import transaction

from .models import Order, Position
from .adapters.dhan import DhanAdapter
from django.conf import settings
class OrderManagementSystem:

    @transaction.atomic
    def create_order(
        self,
        user,
        security_id,
        symbol,
        side,
        quantity,
        order_type="MARKET",
        price=0,
        mode="VIRTUAL",
    ):

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        if side not in ["BUY", "SELL"]:
            raise ValueError(
                "Invalid order side"
            )

        if mode not in ["VIRTUAL", "LIVE"]:
            raise ValueError(
                "Invalid order mode"
            )

        order = Order.objects.create(
            user=user,
            security_id=security_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            mode=mode,
            status="PENDING",
        )

        return order

    def execute_virtual_order(self, order):

        price = Decimal(order.price)

        position, _ = Position.objects.get_or_create(
            user=order.user,
            security_id=order.security_id,
            defaults={
                "symbol": order.symbol,
                "quantity": 0,
                "average_price": 0,
            },
        )

        if order.side == "BUY":

            old_quantity = position.quantity
            old_average = position.average_price

            new_quantity = (
                old_quantity + order.quantity
            )

            if new_quantity > 0:

                total_value = (
                    old_quantity * old_average
                    + order.quantity * price
                )

                position.average_price = (
                    total_value / new_quantity
                )

            position.quantity = new_quantity

        elif order.side == "SELL":

            if order.quantity > position.quantity:

                order.status = "FAILED"

                order.error_message = (
                    "Insufficient position quantity"
                )

                order.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "updated_at",
                    ]
                )

                return

            position.quantity -= order.quantity

            if position.quantity == 0:
                position.average_price = 0

        position.save()

        order.status = "EXECUTED"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def get_broker_adapter(self, user):

        return DhanAdapter(user)

    def get_proxy(self, user):
        return ProxyService().get_user_proxy(user)

    def select_proxy(self, order):

        proxy = self.get_proxy(order.user)

        order.proxy_ip = proxy["public_ip"]
        order.proxy_port = proxy["port"]

        order.status = "PROXY_SELECTED"

        order.save(
            update_fields=[
                "proxy_ip",
                "proxy_port",
                "status",
                "updated_at",
            ]
        )

        return proxy

    def build_broker_payload(self, order):

        adapter = self.get_broker_adapter(
            order.user
        )

        return adapter.build_order_payload(
            security_id=order.security_id,
            quantity=order.quantity,
            side=order.side,
            order_type=order.order_type,
            price=float(order.price),
        )

    def execute(self, order):

        proxy = self.select_proxy(order)

        payload = self.build_broker_payload(order)

        if order.mode == "VIRTUAL":
            return self.execute_virtual_order(order)

        return self.execute_live_order(
            order,
            proxy,
            payload,
        )

    def execute_virtual_order(self, order):

        try:
            # Existing virtual position logic here

            order.status = "EXECUTED"

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return order

        except Exception as exc:

            order.status = "FAILED"
            order.error_message = str(exc)

            order.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

            raise


    def execute_live_order(
        self,
        order,
        proxy,
        payload,
    ):

        if not settings.LIVE_TRADING_ENABLED:
            raise RuntimeError(
                "Live trading is disabled"
            )

        # Actual broker call will be added later.