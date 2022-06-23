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


class UserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "following", "followers"]

    def get_following(self, obj: Any) -> Any:
        return FollowingSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj: Any) -> Any:
        return FollowersSerializer(obj.followers.all(), many=True).data


class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="following_user_id.username")

    class Meta:
        model = UserFollowing
        fields = ["following_user_id", "username", "created_at"]


class FollowersSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user_id.username")

    class Meta:
        model = UserFollowing
        fields = ["user_id", "username", "created_at"]
