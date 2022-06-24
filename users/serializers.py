from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserFollowing

User = get_user_model()


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore
    @classmethod
    def get_token(cls: Any, user: Any) -> Any:
        token = super().get_token(user)
        token["userID"] = user.id
        token["editor"] = user.is_editor
        return token


class UserFollowingSerializer(serializers.ModelSerializer):
    followed = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "followed", "followers"]

    def get_followed(self, obj: Any) -> Any:
        return FollowedSerializer(obj.followed.all(), many=True).data

    def get_followers(self, obj: Any) -> Any:
        return FollowersSerializer(obj.followers.all(), many=True).data


class FollowedSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="followed.username")

    class Meta:
        model = UserFollowing
        fields = ["followed", "username", "created_at"]


class FollowersSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="follower.username")

    class Meta:
        model = UserFollowing
        fields = ["follower", "username", "created_at"]
