from typing import Any

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.utils import (
    create_email_data,
    generate_token,
    send_email,
    verify_token,
)

from .models import Profile, UserFollowing
from .validators import (
    validate_password_digit,
    validate_password_lowercase,
    validate_password_symbol,
    validate_password_uppercase,
)

User = get_user_model()


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore
    @classmethod
    def get_token(cls: Any, user: Any) -> Any:
        token = super().get_token(user)
        token["userID"] = user.lookup_id
        token["editor"] = user.is_editor
        return token


class UserSerializer(serializers.ModelSerializer):
    lookup_id = serializers.CharField(read_only=True)
    username = serializers.CharField(
        max_length=20,
        min_length=5,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        min_length=6,
        max_length=128,
        write_only=True,
        validators=[
            validate_password_digit,
            validate_password_uppercase,
            validate_password_symbol,
            validate_password_lowercase,
        ],
    )

    class Meta:
        model = User
        fields = ("lookup_id", "username", "email", "password")

    def to_representation(self, instance: Any) -> Any:
        representation = super().to_representation(instance)
        representation["lookup_id"] = str(instance.lookup_id)
        return super().to_representation(instance)

    def create(self, validated_data: Any) -> Any:
        user = User.objects.create_user(**validated_data)
        user.save()
        Profile.objects.create(user=user)
        token_data = generate_token(user)
        request = self.context.get("request")
        email_data = create_email_data(
            request, user, token_data, "verify-email", "Verify your email"  # type: ignore[arg-type]
        )
        send_email("verify_email.html", email_data)
        return user


class VerifyEmailSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs: Any) -> Any:
        uidb64 = attrs["uidb64"]
        token = attrs["token"]
        if verify_token(uidb64, token):
            return attrs
        raise serializers.ValidationError("failed to verify")

    def save(self, **kwargs: Any) -> Any:
        uidb64 = self.validated_data.get("uidb64")
        user_id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(lookup_id=user_id)
        user.is_verified = True
        user.save()


class CreateFollowingSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(
        slug_field="lookup_id", queryset=User.objects.all()
    )
    followed = serializers.SlugRelatedField(
        slug_field="lookup_id", queryset=User.objects.all()
    )

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
        user = User.objects.filter(email=attrs["email"]).first()
        if user:
            token_data = generate_token(user)
            request = self.context.get("request")
            email_data = create_email_data(
                request, user, token_data, "reset-password", "Password Reset"  # type: ignore[arg-type]
            )
            send_email("reset_password.html", email_data)

        return super().validate(attrs)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6,
        max_length=128,
        write_only=True,
        validators=[
            validate_password_digit,
            validate_password_uppercase,
            validate_password_symbol,
            validate_password_lowercase,
        ],
    )
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    class Meta:
        fields = ["password", "uidb64", "token"]

    def validate(self, attrs: Any) -> Any:
        uidb64 = attrs.get("uidb64")
        token = attrs.get("token")
        if verify_token(uidb64, token):
            return attrs
        raise serializers.ValidationError(
            {"detail": "failed to reset password"}
        )

    def save(self, **kwargs: Any) -> Any:
        uidb64 = self.validated_data.get("uidb64")
        password = self.validated_data.get("password")
        user_id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(lookup_id=user_id)
        user.set_password(password)
        user.save()
