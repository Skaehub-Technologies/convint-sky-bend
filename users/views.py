from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserTokenObtainPairSerializer,
)

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer


class PasswordResetEmailView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:

        serializer = self.get_serializer(
            data={"email": request.data.get("email")}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "check your email for password reset link"},
            status=status.HTTP_200_OK,
        )


class PasswordResetAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def patch(self, request: Any, uidb64: Any, token: Any) -> Any:
        serializer = self.get_serializer(
            data={**request.data, "uidb64": uidb64, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password changed successfully"},
            status=status.HTTP_200_OK,
        )
