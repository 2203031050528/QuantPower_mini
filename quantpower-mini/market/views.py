from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Instrument
from .serializers import InstrumentSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class InstrumentListView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = InstrumentSerializer

    queryset = Instrument.objects.filter(
        is_active=True
    ).order_by("symbol")


from .redis_service import get_tick


class LatestTickView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, security_id):

        tick = get_tick(security_id)

        if not tick:
            return Response(
                {
                    "message": "No market data available"
                },
                status=404,
            )

        return Response(tick)