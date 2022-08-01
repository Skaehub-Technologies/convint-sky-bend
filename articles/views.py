from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from articles.models import Article, Comment
from articles.permissions import IsAuthorEditorOrReadOnly
from articles.serializers import ArticleSerializer, CommentSerializer
from articles.validators import validate_index
from users.models import Profile


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


class CommentListView(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    queryset = Article.objects.all()
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, slug: str) -> Response:
        """
        Allows authenticated users can add comments on articles
        Args:
            slug: this a slug for a particular article
        Returns:
            code: The return 201 created for success
        """
        self.author = get_object_or_404(Profile, user=request.user)
        self.article = get_object_or_404(Article, slug=slug)
        start_index = validate_index(request.data.get("highlight_start"), slug)
        end_index = validate_index(request.data.get("highlight_end"), slug)
        if start_index and end_index:
            selected = (
                [int(start_index), int(end_index)]
                if start_index < end_index
                else [int(end_index), int(start_index)]
            )
            highlight_text = str(self.article.body[selected[0] : selected[1]])
            request.data["highlight_text"] = highlight_text
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.author, article=self.article)
        return Response(
            {
                "message": "Comment added successfully",
                "comment": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request: Request, slug: str) -> Response:
        """
        get all comments on an article
        Args:
            param1 (slug): this a slug for a particular article
        Returns:
            code: The return 201 created for success
        """
        self.article = get_object_or_404(Article, slug=slug)
        comments = Comment.objects.filter(article=self.article)
        comment_count = comments.count()
        serializer = self.serializer_class(comments, many=True)
        return Response(
            {
                "message": "Comments fetched successfully",
                "comments": serializer.data,
                "comment_count": comment_count,
            },
            status=status.HTTP_201_CREATED,
        )


class CommentDetailView(generics.GenericAPIView):
    serializer_class = CommentSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = (IsAuthorEditorOrReadOnly,)

    def get(self, request: Request, slug: str, lookup_id: str) -> Response:
        """
        get a comment on an article
        Args:
            slug: this a slug for a particular article
            lookup_id: this is the id of the comment
        Returns:
            code: The return 200 created for success
        """
        self.comment = get_object_or_404(Comment, lookup_id=lookup_id)
        serializer = self.serializer_class(self.comment)
        return Response(
            {
                "message": "Comment fetched successfully",
                "comment": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request: Request, slug: str, lookup_id: str) -> Response:
        """
        update a comment on an article
        Args:
            slug: this a slug for a particular article
            lookup_id: this is the id of the comment
        Returns:
            code: The return 201 created for success
        """
        self.comment = get_object_or_404(Comment, lookup_id=lookup_id)
        self.comment.body = request.data.get("body")  # type: ignore[assignment]
        self.comment.save()
        serializer = self.serializer_class(self.comment)
        return Response(
            {
                "message": "Comment updated successfully",
                "comment": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, slug: str, lookup_id: str) -> Response:
        """
        delete a comment on an article
        Args:
            slug: this a slug for a particular article
            lookup_id: this is the id of the comment
        Returns:
            code: The return 200 deleted for success
        """
        self.comment = get_object_or_404(Comment, lookup_id=lookup_id)
        self.comment.delete()
        return Response(
            {"message": "Comment deleted successfully"},
            status=status.HTTP_200_OK,
        )
