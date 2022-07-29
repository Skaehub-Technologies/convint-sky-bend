from typing import Any

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from articles.models import Article
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import (  # type: ignore[attr-defined]
    ArticleFavoriteSerializer,
    ArticleSerializer,
    ArticleUnFavoriteSerializer,
)


class ArticleListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorEditorOrReadOnly,)
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """return custom response for DELETE request"""
        self.destroy(request, *args, **kwargs)
        return Response(
            {"message": "Article deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class ArticleFavoriteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleFavoriteSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)


class ArticleUnFavoriteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleUnFavoriteSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)
