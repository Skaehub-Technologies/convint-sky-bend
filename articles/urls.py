from django.urls import path

from articles.views import ArticleDetailView, ArticleListView

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path(
        "articles/<slug:slug>/detail/",
        ArticleDetailView.as_view(),
        name="article-detail",
    ),
    path(
        "articles/<slug:slug>/delete/",
        ArticleDetailView.as_view(),
        name="article-delete",
    ),
    path(
        "articles/<slug:slug>/edit/",
        ArticleDetailView.as_view(),
        name="article-edit",
    ),
]
