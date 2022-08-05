from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from articles.models import Article, Comment
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import (  # type: ignore[attr-defined]
    ArticleSerializer,
    CommentSerializer,
    FavoriteSerializer,
    UnFavoriteSerializer,
)

User = get_user_model()


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


class CommentListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    renderer_classes = (JSONRenderer,)

    def get_queryset(self) -> Any:
        return (
            super()
            .get_queryset()
            .filter(article__slug=self.kwargs.get("slug"))
        )

    def post(self, request: Request, slug: str, *args, **kwargs) -> Response:  # type: ignore[no-untyped-def,override]
        """
        Allows authenticated users can add comments on articles
        Args:
            slug: this a slug for a particular article
        Returns:
            code: The return 201 created for success
        """
        request.data["article"] = slug
        return self.create(request, *args, **kwargs)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    renderer_classes = (JSONRenderer,)
    queryset = Comment.objects.all()
    permission_classes = (IsAuthorEditorOrReadOnly,)
    lookup_field: str = "lookup_id"
