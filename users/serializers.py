from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed,
    ParseError,
    PermissionDenied,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.settings.base import EMAIL_USER
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("lookup_id", "username", "email", "password")

    def create(self, validated_data: Any) -> Any:
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        send_mail(
            "Registration Successful",
            "You have successfully regsitered your accout",
            EMAIL_USER,
            [user.email],
        )
        return user


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
