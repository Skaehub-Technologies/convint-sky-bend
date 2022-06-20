from multiprocessing import AuthenticationError
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
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


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ["email"]


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, min_length=6)
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    class Meta:
        fields = ["password", "uidb64", "token"]

    def validate(self, attrs: Any) -> Any:
        try:

            password = attrs.get("password")
            uidb64 = attrs.get("uidb64")
            token = attrs.get("token")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationError("Invalid Token", 401)

            user.set_password(password)
            user.save()

        except Exception:
            raise AuthenticationError("Invalid Token", 401)
        return super().validate(attrs)


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


class UserFollowingSerializer(serializers.ModelSerializer):
    following = serializers.ReadOnlyField(source="following_user_id.username")
    follower = serializers.ReadOnlyField(source="user_id.username")

    class Meta:
        model = UserFollowing
        fields = ["id", "created_at", "following", "follower"]


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
