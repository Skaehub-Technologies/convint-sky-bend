from typing import Any
from .models import  Profile


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore
    @classmethod
    def get_token(cls: Any, user: Any) -> Any:
        token = super().get_token(user)
        token["userID"] = user.id
        token["editor"] = user.is_editor
        return token


class ProfileSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = Profile
        fields = '__all__'
