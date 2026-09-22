from django.conf import settings
from django.db import models


class EIPPool(models.Model):

    public_ip = models.GenericIPAddressField(
        unique=True
    )

    private_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    is_allocated = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.public_ip


class ProxyAllocation(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="proxy_allocation",
    )

    eip = models.ForeignKey(
        EIPPool,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    proxy_port = models.PositiveIntegerField(
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.user.username} → "
            f"{self.eip.public_ip}:{self.proxy_port}"
        )