from rest_framework import serializers
from .models import DhanAccount


class DhanAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = DhanAccount
        fields = [
            "id",
            "client_id",
            "access_token",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]