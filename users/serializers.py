from typing import Any

# from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.settings.base import EMAIL_USER

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
        fields = ("id", "username", "email", "password")

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
