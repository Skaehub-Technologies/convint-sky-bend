from typing import Any

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from articles.models import Article
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import ArticleSerializer


class ArticleListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthorEditorOrReadOnly]
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """return custom response for DELETE request"""
        self.destroy(request, *args, **kwargs)
        return Response(
            {"message": "Article deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
