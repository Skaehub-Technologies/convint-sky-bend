import django_filters
from django_filters import FilterSet

from articles.models import Article


class AuthorFilter(FilterSet):  # type:ignore[no-any-unimported]
    author__username = django_filters.CharFilter(
        field_name="author", lookup_expr="icontains"
    )

    class Meta:
        model = Article
        fields = ["favorited", "body", "title", "description", "author"]
