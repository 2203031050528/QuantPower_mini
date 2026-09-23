from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import ProxyService


class ProxyStatusView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        try:
            proxy = ProxyService().get_user_proxy(
                request.user
            )

            return Response({
                "active": True,
                "proxy": proxy,
            })

        except ValueError as exc:

            return Response({
                "active": False,
                "error": str(exc),
            })