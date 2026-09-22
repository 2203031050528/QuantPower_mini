from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DhanAccount
from .serializers import DhanAccountSerializer


class DhanAccountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            account = DhanAccount.objects.get(user=request.user)

        except DhanAccount.DoesNotExist:
            return Response(
                {"message": "Dhan account not connected"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            DhanAccountSerializer(account).data
        )

    def post(self, request):

        account, created = DhanAccount.objects.update_or_create(
            user=request.user,
            defaults={
                "client_id": request.data.get("client_id"),
                "access_token": request.data.get("access_token"),
                "is_active": True,
            }
        )

        return Response(
            DhanAccountSerializer(account).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )