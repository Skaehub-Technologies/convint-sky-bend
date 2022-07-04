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

        # check if user is the same as the one you are trying to follow
        if user.id == pk:
            return Response(
                {"details": "you cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if user is already following the user you are trying to follow
        if UserFollowing.objects.filter(
            follower=user, followed_id=pk
        ).exists():
            return Response(
                {"details": "you are already following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = self.get_object(pk)
        UserFollowing.objects.create(follower=user, followed=follow)
        serializer = UserFollowingSerializer(follow)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
