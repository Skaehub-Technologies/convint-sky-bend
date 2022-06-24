from typing import Any

from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserFollowing,
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
        return Response(serializer.data)

    def post(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        UserFollowing.objects.create(follower=user, followed=follow)
        serializer = UserFollowingSerializer(follow)
        return Response(serializer.data)

    def delete(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        connection = UserFollowing.objects.filter(
            follower=user, followed=follow
        ).first()
        if connection:
            connection.delete()
        serializer = UserFollowingSerializer(follow)
        return Response(serializer.data)
