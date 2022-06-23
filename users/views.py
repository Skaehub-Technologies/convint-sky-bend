from typing import Any

from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserFollowing,
    UserSerializer,
    UserTokenObtainPairSerializer,
)

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer


class UserFollow(APIView):
    def get_object(self, pk: Any) -> Any:
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = self.get_object(pk)
        print(user)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        UserFollowing.objects.create(user_id=user, following_user_id=follow)
        serializer = UserSerializer(follow)
        return Response(serializer.data)

    def delete(self, request: Any, pk: Any, format: Any = None) -> Any:
        user = request.user
        follow = self.get_object(pk)
        connection = UserFollowing.objects.filter(
            user_id=user, following_user_id=follow
        ).first()
        if connection:
            connection.delete()
        serializer = UserSerializer(follow)
        return Response(serializer.data)
