from typing import Any

from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import UserFollowing

from .serializers import (
    CreateFollowingSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserFollowingSerializer,
    UserTokenObtainPairSerializer,
)

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer


class UserFollowView(APIView):
    def get_object(self, pk: Any) -> Any:
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = self.get_object(pk)
        serializer = UserFollowingSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        serializer = CreateFollowingSerializer(
            data={"follower": user.id, "followed": follow.id}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            serializer_two = UserFollowingSerializer(follow)
            return Response(serializer_two.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        connection = UserFollowing.objects.filter(
            follower=user, followed=follow
        ).first()
        if connection:
            connection.delete()
        serializer = UserFollowingSerializer(follow)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
