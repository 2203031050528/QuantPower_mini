from django.conf import settings
from django.db import models


class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROXY_SELECTED", "Proxy Selected"),
        ("SENT_TO_DHAN", "Sent to Dhan"),
        ("EXECUTED", "Executed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    MODE_CHOICES = [
        ("VIRTUAL", "Virtual"),
        ("LIVE", "Live"),
    ]

    SIDE_CHOICES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    ]

    ORDER_TYPE_CHOICES = [
        ("MARKET", "Market"),
        ("LIMIT", "Limit"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    security_id = models.CharField(max_length=50)
    symbol = models.CharField(max_length=100)

    side = models.CharField(
        max_length=10,
        choices=SIDE_CHOICES,
    )

    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPE_CHOICES,
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default="VIRTUAL",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    broker_order_id = models.CharField(
        max_length=100,
        blank=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    proxy_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    proxy_port = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
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