from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data: Any) -> Any:
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'bio', 'image')