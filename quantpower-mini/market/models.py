from django.db import models


class Instrument(models.Model):
    exchange = models.CharField(max_length=20)
    segment = models.CharField(max_length=30)

    security_id = models.CharField(
        max_length=50,
        unique=True
    )

    symbol = models.CharField(max_length=100)

    instrument_type = models.CharField(
        max_length=30,
        blank=True
    )

    expiry = models.DateField(
        null=True,
        blank=True
    )

    strike_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    option_type = models.CharField(
        max_length=5,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} ({self.security_id})"