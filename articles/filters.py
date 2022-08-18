import django_filters
from django_filters import FilterSet

from articles.models import Article


class ArticleFilter(FilterSet):  # type:ignore[no-any-unimported]
    author = django_filters.CharFilter(
        field_name="author__username", lookup_expr="icontains"
    )
    tags = django_filters.CharFilter(
        field_name="tags__name", lookup_expr="icontains"
    )

    class Meta:
        model = Article
        fields = ["tags", "author"]
