from django.urls import path

from articles.views import (
    ArticleDetailView,
    ArticleListView,
    CommentDetailView,
    CommentListView,
    ArticleFavoriteView,
    ArticleUnFavoriteView,
)

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path(
        "articles/<slug:slug>/detail/",
        ArticleDetailView.as_view(),
        name="article-detail",
    ),
    path(
        "articles/<slug:slug>/comments/",
        CommentListView.as_view(),
        name="comments",
    ),
    path(
        "articles/<slug:slug>/comments/<str:lookup_id>/",
        CommentDetailView.as_view(),
        name="comment-detail",
    ),
    path("articles/<slug:slug>/favorite/",
        ArticleFavoriteView.as_view(),
        name="article-favorite",
    ),
    path(
        "articles/<slug:slug>/unfavorite/",
        ArticleUnFavoriteView.as_view(),
        name="article-unfavorite",
    ),
]
