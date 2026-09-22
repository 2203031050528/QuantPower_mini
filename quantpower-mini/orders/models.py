from django.conf import settings
from django.db import models


class Order(models.Model):

    ORDER_TYPES = [
        ("MARKET", "Market"),
        ("LIMIT", "Limit"),
    ]

    SIDES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    ]

    MODES = [
        ("VIRTUAL", "Virtual"),
        ("LIVE", "Live"),
    ]

    STATUSES = [
        ("PENDING", "Pending"),
        ("EXECUTED", "Executed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    security_id = models.CharField(max_length=50)

    symbol = models.CharField(max_length=100)

    side = models.CharField(
        max_length=10,
        choices=SIDES,
    )

    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPES,
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    mode = models.CharField(
        max_length=10,
        choices=MODES,
        default="VIRTUAL",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default="PENDING",
    )

    broker_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.symbol} - "
            f"{self.side} - "
            f"{self.quantity}"
        )


class Position(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="positions",
    )

    security_id = models.CharField(max_length=50)

    symbol = models.CharField(max_length=100)

    quantity = models.IntegerField(default=0)

    average_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    realized_pnl = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "security_id",
                ],
                name="unique_user_position",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.symbol} - "
            f"{self.quantity}"
        )