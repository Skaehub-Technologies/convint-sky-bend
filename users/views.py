from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Profile
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    UserTokenObtainPairSerializer,
)

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer


class ProfileView(UpdateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def post(self, request: Any) -> Any:
        current_user = request.user
        data = request.data
        profile = Profile.objects.filter(user=current_user.pk)
        if profile:
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        else:
            serializer = ProfileSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=current_user)
                new_data = serializer.data
                return Response(new_data)
            return Response(serializer.errors)


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

    def patch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        serializer = self.get_serializer(
            data={
                **request.data,
                "uidb64": kwargs.get("uidb64"),
                "token": kwargs.get("token"),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password changed successfully"},
            status=status.HTTP_200_OK,
        )
