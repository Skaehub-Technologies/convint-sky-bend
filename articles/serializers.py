# type: ignore[union-attr]

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from articles.models import Article
from users.serializers import UserSerializer

User = get_user_model()


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):  # type: ignore[no-any-unimported]
    author = UserSerializer(read_only=True)
    image = serializers.ImageField(
        use_url=True, required=False, allow_null=True
    )
    tags = TagListSerializerField()
    title = serializers.CharField(max_length=255, min_length=10)
    body = serializers.CharField(required=True, min_length=50)
    likes = UserSerializer(many=True, required=False, read_only=True)
    dislikes = UserSerializer(many=True, required=False, read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "lookup_id",
            "slug",
            "title",
            "description",
            "image",
            "body",
            "tags",
            "is_hidden",
            "likes_count",
            "dislikes_count",
            "likes",
            "dislikes",
            "created_at",
            "updated_at",
            "author",
        )
        read_only_fields = [
            "created_at",
            "updated_at",
            "author",
            "likes",
            "dislikes",
        ]

    def get_likes_count(self, instance: Any) -> Any:
        return instance.likes.count()

    def get_dislikes_count(self, instance: Any) -> Any:
        return instance.dislikes.count()

    def create(self, validated_data: Any) -> Any:
        """set current user as author"""
        validated_data["author"] = self.context.get("request").user
        return super().create(validated_data)

    def to_representation(self, instance: Any) -> Any:
        """check if the user liked or disliked an article and return favorited and unfavorited status"""
        request = self.context.get("request")
        representation = super().to_representation(instance)
        if request.user.is_authenticated:
            if request.user in instance.likes.all():
                return {
                    **representation,
                    "favorited": True,
                    "unfavorited": False,
                }
            if request.user in instance.dislikes.all():
                return {
                    **representation,
                    "favorited": False,
                    "unfavorited": True,
                }
            return {**representation, "favorited": False, "unfavorited": False}
        return representation


class ArticleFavoriteSerializer(serializers.ModelSerializer):
    likes = UserSerializer(many=True, required=False, read_only=True)
    dislikes = UserSerializer(many=True, required=False, read_only=True)
    tags = TagListSerializerField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "lookup_id",
            "slug",
            "title",
            "description",
            "image",
            "body",
            "tags",
            "is_hidden",
            "likes_count",
            "dislikes_count",
            "likes",
            "dislikes",
            "created_at",
            "updated_at",
            "author",
        )
        read_only_fields = [
            "lookup_id",
            "slug",
            "title",
            "description",
            "image",
            "body",
            "tags",
            "is_hidden",
            "likes_count",
            "dislikes_count",
            "created_at",
            "updated_at",
            "author",
        ]

    def get_likes_count(self, instance: Any) -> Any:
        return instance.likes.count()

    def get_dislikes_count(self, instance: Any) -> Any:
        return instance.dislikes.count()


class ArticleFavoriteSerializer(ArticleFavoriteSerializer):
    def update(self, instance: Any, validated_data: Any) -> Any:
        """update the likes of an article"""
        request = self.context.get("request")

        if request.user in instance.likes.all():
            instance.likes.remove(request.user)
            return instance
        if request.user in instance.dislikes.all():
            instance.dislikes.remove(request.user)
        instance.likes.add(request.user)
        return instance

    def to_representation(self, instance: Any) -> Any:

        """check if the user liked or disliked an article and return favorited and unfavorited status"""
        request = self.context.get("request")
        representation = super().to_representation(instance)

        if request.user in instance.likes.all():
            return {
                **representation,
                "favorited": True,
                "unfavorited": False,
            }
        return {**representation, "favorited": False, "unfavorited": False}


class ArticleUnFavoriteSerializer(ArticleFavoriteSerializer):
    def update(self, instance: Any, validated_data: Any) -> Any:
        """update the dislikes of an article"""
        request = self.context.get("request")

        if request.user in instance.dislikes.all():
            instance.dislikes.remove(request.user)
            return instance
        if request.user in instance.likes.all():
            instance.likes.remove(request.user)
        instance.dislikes.add(request.user)
        return instance

    def to_representation(self, instance: Any) -> Any:
        """check if the user liked or disliked an article and return favorited and unfavorited status"""
        request = self.context.get("request")
        representation = super().to_representation(instance)
        if request.user in instance.dislikes.all():
            return {
                **representation,
                "favorited": False,
                "unfavorited": True,
            }
        return {**representation, "favorited": False, "unfavorited": False}
