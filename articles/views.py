from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from articles.filters import AuthorFilter
from articles.models import Article
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import (  # type: ignore[attr-defined]
    ArticleSerializer,
    FavoriteSerializer,
    UnFavoriteSerializer,
)


class ArticleListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AuthorFilter

    search_fields = [
        "likes",
        "body",
        "title",
        "description",
        "author__username",
    ]
    ordering_fields = ["-updated_at"]


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


class ArticleFavoriteView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)


class ArticleUnFavoriteView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UnFavoriteSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)
