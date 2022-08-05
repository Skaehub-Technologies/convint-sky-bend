# type: ignore[union-attr]

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from articles.models import Article, Comment
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
            "reading_time",
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
            "reading_time",
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


class FavoriteSerializer(ArticleFavoriteSerializer):
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


class UnFavoriteSerializer(ArticleFavoriteSerializer):
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


class CommentSerializer(serializers.ModelSerializer):
    """
    Serilaizes the comment model
    """

    author = UserSerializer(read_only=True)
    article = serializers.SlugRelatedField(
        queryset=Article.objects.all(), slug_field="slug"
    )
    highlight_start = serializers.IntegerField(min_value=0, required=False)
    highlight_end = serializers.IntegerField(min_value=0, required=False)
    highlight_text = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "lookup_id",
            "body",
            "created_at",
            "updated_at",
            "author",
            "article",
            "highlight_start",
            "highlight_end",
            "highlight_text",
        )
        read_only_fields = ("author", "lookup_id")

    def validate(self, data: Any) -> Any:
        if not data.get("highlight_start") and not data.get("highlight_end"):
            return data
        if data.get("highlight_start") and not data.get("highlight_end"):
            raise serializers.ValidationError(
                {
                    "highlight_end": "This field is required when highlight_start is provided"
                }
            )
        if not data.get("highlight_start") and data.get("highlight_end"):
            raise serializers.ValidationError(
                {
                    "highlight_start": "This field is required when highlight_end is provided"
                }
            )

        article = data.get("article")
        if data.get("highlight_start") > len(article.body):
            raise serializers.ValidationError(
                {
                    "highlight_start": "highlight_start must be less than the length of the article body"
                }
            )
        if data.get("highlight_end") > len(article.body):
            raise serializers.ValidationError(
                {
                    "highlight_end": "highlight_end must be less than the length of the article body"
                }
            )
        return data

    def create(self, validated_data: Any) -> Any:
        """set current user as author"""
        article = validated_data.get("article")
        validated_data["author"] = self.context.get("request").user
        if validated_data.get("highlight_start") and validated_data.get(
            "highlight_end"
        ):
            start_index = validated_data.get("highlight_start")
            end_index = validated_data.get("highlight_end")
            if start_index and end_index:
                selected = (
                    [int(start_index), int(end_index)]
                    if start_index < end_index
                    else [int(end_index), int(start_index)]
                )
                highlight_text = str(article.body[selected[0] : selected[1]])
                validated_data["highlight_text"] = highlight_text

        return super().create(validated_data)
