from typing import Any
from .models import User, Profile


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


# class UserProfile(serializers.Serializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'
#         extra_kwargs = {'password' : {'write_only' : True}}

#     def create(self, validated_data):
#         user = User.objects.create(
#             email = validated_data['email'],
#             username = validated_data['username'],
#             bio = validated_data['bio'],
#             image = validated_data['image']
#         )
#         user.set_password(validated_data['password'])
#         user.save()

#         return user
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source=User)
    bio = serializers.CharField(allow_blank= True, required=False)
    image = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user',)

    def get_image (self, obj):
        if obj.image:
            return obj.image

        return 'https://image.shutterstock.com/image-vector/default-avatar-profile-icon-social-260nw-1677509740.jpg'
            
    
      


