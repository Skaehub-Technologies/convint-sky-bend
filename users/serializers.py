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

from .models import Profile

User = get_user_model()


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore
    @classmethod
    def get_token(cls: Any, user: Any) -> Any:
        token = super().get_token(user)
        token["userID"] = user.id
        token["editor"] = user.is_editor
        return token


class ProfileSerializer(serializers.ModelSerializer):
    user: Any = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Profile
        fields = "__all__"


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
