from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed,
    ParseError,
    PermissionDenied,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.utils import Util

from .models import Profile, UserFollowing

User = get_user_model()


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore
    @classmethod
    def get_token(cls: Any, user: Any) -> Any:
        token = super().get_token(user)
        token["userID"] = user.id
        token["editor"] = user.is_editor
        return token


class ProfileSerializer(serializers.ModelSerializer):
    username: Any = serializers.CharField(
        read_only=True, source="user.username"
    )
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Profile
        fields = ("username", "bio", "image")

    def update(self, instance: Any, validated_data: Any) -> Any:
        instance.bio = validated_data.get("bio")
        instance.image = validated_data.get("image")
        instance.save()
        return instance


class CreateFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ("id", "follower", "followed")

    def validate(self, attrs: Any) -> Any:
        follower = attrs.get("follower")
        followed = attrs.get("followed")
        if follower == followed:
            raise PermissionDenied("you cannot follow yourself")
        if UserFollowing.objects.filter(
            follower=follower, followed=followed
        ).exists():
            raise PermissionDenied("you are already following this user")
        return super().validate(attrs)


class UserFollowingSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "following", "followers"]

    def get_following(self, obj: Any) -> Any:
        return FollowedSerializer(obj.following.all(), many=True).data

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


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ["email"]

    def validate(self, attrs: Any) -> Any:
        try:
            request = self.context.get("request")
            email = attrs.get("email")
            user_data = Util.generate_reset_token(email)

            if user_data:
                email_data = Util.create_reset_email(request, *user_data)
                Util.send_email("reset_password.html", email_data)
        except KeyError:
            raise ParseError("email must be provided")
        return super().validate(attrs)


class PasswordResetSerializer(serializers.Serializer):
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
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Invalid token")

            user.set_password(password)
            user.save()

        except Exception:
            raise PermissionDenied("failed to reset password")
        return super().validate(attrs)
