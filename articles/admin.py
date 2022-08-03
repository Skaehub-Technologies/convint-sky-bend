from django.contrib import admin

from articles.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "author",
        "is_hidden",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "author")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Article, ArticleAdmin)
