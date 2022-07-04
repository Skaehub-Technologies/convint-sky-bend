from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
