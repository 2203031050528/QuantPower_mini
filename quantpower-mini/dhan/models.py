from django.conf import settings
from django.db import models


class DhanAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dhan_account"
    )

    client_id = models.CharField(max_length=100)

    access_token = models.TextField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.client_id}"