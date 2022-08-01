from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from articles.models import Article
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import ArticleSerializer


class ArticleListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "favorited",
        "body",
        "title",
        "is_hidden",
        "description",
    ]
    search_fields = ["favorited", "body", "title", "is_hidden", "description"]
    ordering_fields = ["updated_at"]


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorEditorOrReadOnly,)
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "favorited",
        "body",
        "title",
        "is_hidden",
        "description",
    ]
    search_fields = ["favorited", "body", "title", "is_hidden", "description"]
    ordering_fields = ["updated_at"]

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """return custom response for DELETE request"""
        self.destroy(request, *args, **kwargs)
        return Response(
            {"message": "Article deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
