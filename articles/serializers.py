from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from articles.models import Article, Comment
from users.serializers import ProfileSerializer, UserSerializer

User = get_user_model()


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):  # type: ignore[no-any-unimported]
    author = UserSerializer(read_only=True)
    image = serializers.ImageField(
        use_url=True, required=False, allow_null=True
    )
    tags = TagListSerializerField()
    title = serializers.CharField(max_length=255, min_length=10)
    body = serializers.CharField(required=True, min_length=50)

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
            "favorited",
            "favoritesCount",
            "created_at",
            "updated_at",
            "author",
        )
        read_only_fields = [
            "created_at",
            "updated_at",
            "author",
            "favoritesCount",
        ]

    def create(self, validated_data: Any) -> Any:
        """set current user as author"""
        validated_data["author"] = self.context.get("request").user  # type: ignore[union-attr]
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """
    Serilaizes the comment model
    """

    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "lookup_id",
            "body",
            "created_at",
            "updated_at",
            "author",
            "highlight_start",
            "highlight_end",
            "highlight_text",
        )
        read_only_fields = ("author",)
