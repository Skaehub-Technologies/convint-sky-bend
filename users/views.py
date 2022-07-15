from typing import Any

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import UserFollowing

from .models import Profile
from .permissions import CanRegisterbutcantGetList
from .serializers import (
    CreateFollowingSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    UserFollowingSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
    VerifyEmailSerializer,
)

User = get_user_model()


class UserList(generics.ListCreateAPIView):
    permission_classes = (CanRegisterbutcantGetList,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)


class ProfileView(RetrieveUpdateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field: str = "lookup_id"
    renderer_classes = (JSONRenderer,)

    def get_object(self) -> Any:
        profile = get_object_or_404(
            self.get_queryset(), user__lookup_id=self.kwargs.get("lookup_id")
        )

        return profile


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CanRegisterbutcantGetList,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field: str = "lookup_id"
    renderer_classes = (JSONRenderer,)


class VerifyEmail(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyEmailSerializer
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(
            data={
                **request.data,
                "uidb64": kwargs.get("uidb64"),
                "token": kwargs.get("token"),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("Your email is verified", status=status.HTTP_200_OK)


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer
    renderer_classes = (JSONRenderer,)


class UserFollowView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_field: str = "lookup_id"
    renderer_classes = (JSONRenderer,)
    serializer_class = UserFollowingSerializer
    queryset = User.objects.all()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        follow = self.get_object()
        serializer = CreateFollowingSerializer(
            data={"follower": user.lookup_id, "followed": follow.lookup_id}  # type: ignore[union-attr]
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_two = self.get_serializer(follow)
        return Response(serializer_two.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        follow = self.get_object()
        connection = UserFollowing.objects.filter(  # type: ignore[misc]
            follower=user, followed=follow
        ).first()
        if connection:
            connection.delete()
        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetEmailView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        serializer = self.get_serializer(
            data={"email": request.data.get("email")}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "check your email for password reset link"},
            status=status.HTTP_200_OK,
        )


class PasswordResetAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer
    renderer_classes = (JSONRenderer,)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(
            data={
                **request.data,
                "uidb64": kwargs.get("uidb64"),
                "token": kwargs.get("token"),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "password changed successfully"},
            status=status.HTTP_200_OK,
        )
