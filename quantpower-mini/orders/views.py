from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Order, Position
from .oms import OrderManagementSystem
from .serializers import (
    OrderSerializer,
    PositionSerializer,
)


class OrderCreateView(generics.CreateAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = OrderSerializer

    def perform_create(self, serializer):

        data = serializer.validated_data

        oms = OrderManagementSystem()

        order = oms.create_order(
            user=self.request.user,
            security_id=data["security_id"],
            symbol=data["symbol"],
            side=data["side"],
            quantity=data["quantity"],
            price=data["price"],
            mode=data.get("mode", "VIRTUAL"),
            order_type=data.get(
                "order_type",
                "MARKET",
            ),
        )

        serializer.instance = order


class OrderListView(generics.ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = OrderSerializer

    def get_queryset(self):

        return Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class PositionListView(generics.ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = PositionSerializer

    def get_queryset(self):

        return Position.objects.filter(
            user=self.request.user
        ).order_by("symbol")


from rest_framework.response import Response
from rest_framework.views import APIView

from .adapters.dhan import DhanAdapter


class DhanOrderPreviewView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        adapter = DhanAdapter(
            request.user
        )

        payload = adapter.build_order_payload(
            security_id=request.data["security_id"],
            quantity=request.data["quantity"],
            side=request.data["side"],
            order_type=request.data.get(
                "order_type",
                "MARKET",
            ),
            price=request.data.get(
                "price",
                0,
            ),
        )

        return Response({
            "dry_run": True,
            "broker": "DHAN",
            "payload": payload,
        })