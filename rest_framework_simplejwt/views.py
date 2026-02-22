from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class TokenRefreshView(APIView):
    """Minimal refresh endpoint fallback."""

    permission_classes = []

    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"access": f"dev-access-token-{refresh}"}, status=status.HTTP_200_OK)
