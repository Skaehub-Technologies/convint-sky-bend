import uuid
from typing import Any

from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from taggit.managers import TaggableManager

from users.abstracts import TimeStampedModel
from users.models import Profile

User = get_user_model()


class Article(TimeStampedModel):

    lookup_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, max_length=255
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    image = CloudinaryField("post_images", blank=True, null=True)
    body = models.TextField(blank=False, null=False)
    tags = TaggableManager()
    is_hidden = models.BooleanField(default=False)
    favorited = models.BooleanField(default=False)
    favoritesCount = models.IntegerField(
        blank=True, default=0, validators=[MinValueValidator(0)]
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="author", null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


@receiver(pre_save, sender=Article)
def slug_pre_save(sender: Any, instance: Any, **kwargs: Any) -> None:
    if instance.slug is None or instance.slug == "":
        instance.slug = slugify(f"{instance.title}-{instance.lookup_id}")


class Comment(models.Model):
    """
    Handles CRUD on a comment that has been made on article
    """

    lookup_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, max_length=255
    )
    body = models.TextField(max_length=500, blank=False, null=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    highlight_start = models.PositiveIntegerField(null=True, blank=True)
    highlight_end = models.PositiveIntegerField(null=True, blank=True)
    highlight_text = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="authored"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article"
    )

    class Meta:
        ordering = ["-createdAt"]

    def __str__(self) -> str:
        return self.body
