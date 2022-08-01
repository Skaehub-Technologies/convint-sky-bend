from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from articles.models import Article


def validate_index(index: Any, slug: str) -> Any:
    article = get_object_or_404(Article, slug=slug)
    article_length = len(article.body)
    if index is None:
        return
    if int(index) > article_length:
        raise serializers.ValidationError(
            "Index must not exceed article length."
        )
    return index
