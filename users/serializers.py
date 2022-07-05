from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_str, smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed,
    ParseError,
    PermissionDenied,
)
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.settings.base import EMAIL_USER
from users.utils import Util

from .models import Profile
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
        token["userID"] = user.id
        token["editor"] = user.is_editor
        return token


class UserSerializer(serializers.ModelSerializer):
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
    lookup_id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("lookup_id", "username", "email", "password")

    @staticmethod
    def send_email(user: Any, request: Any) -> None:
        current_site_info = get_current_site(request)
        email_body = render_to_string(
            "verify_email.html",
            {
                "user": user,
                "domain": current_site_info.domain,
                "uid": urlsafe_base64_decode(force_str(user.lookup_id)),
                "token": PasswordResetTokenGenerator().make_token(user),
            },
        )
        send_mail(
            "Verify your email address",
            email_body,
            EMAIL_USER,
            [user.email],
            fail_silently=False,
        )

    def create(self, validated_data: Any) -> Any:
        user = User.objects.create_user(**validated_data)
        user.save()
        Profile.objects.create(user=user)
        self.send_email(user, self.context.get("request"))
        return user


class VerifyEmailSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs: Any) -> Any:
        uidb64 = attrs["uidb64"]
        token = attrs["token"]
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            raise ParseError("Invalid token.") from e
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ParseError("Invalid token.")
        return attrs

    def update(self, instance: Any, validated_data: Any) -> Any:
        instance.is_active = True
        instance.save()
        return instance


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
