from django.contrib.auth import base_user
from decimal import Decimal

from django.db import transaction

from .models import Order, Position
from .adapters.dhan import DhanAdapter

class OrderManagementSystem:

    @transaction.atomic
    def create_order(
        self,
        user,
        security_id,
        symbol,
        side,
        quantity,
        price,
        mode="VIRTUAL",
        order_type="MARKET",
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
            price=price,
            mode=mode,
            order_type=order_type,
            status="PENDING",
        )

        if mode == "VIRTUAL":

            self.execute_virtual_order(order)

        else:

            adapter = self.get_broker_adapter(user)

            payload = adapter.build_order_payload(
                security_id=security_id,
                quantity=quantity,
                side=side,
                order_type=order_type,
                price=price or 0,
            )
            # IMPORTANT:
            # Do not send to Dhan yet.
            #
            # adapter.send_order(payload)

            order.status = "PENDING"

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
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