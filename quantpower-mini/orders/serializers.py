from rest_framework import serializers

from .models import Order, Position


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"

        read_only_fields = [
            "user",
            "status",
            "broker_order_id",
            "error_message",
            "created_at",
            "updated_at",
        ]


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = "__all__"

        read_only_fields = [
            "user",
            "realized_pnl",
            "updated_at",
        ]