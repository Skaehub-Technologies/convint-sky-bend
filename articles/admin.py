from django.contrib import admin

from articles.models import Article, Comment


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


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "body",
        "highlight_start",
        "highlight_end",
        "highlight_text",
        "author",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("article", "author")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


admin.site.register(Comment, CommentAdmin)
