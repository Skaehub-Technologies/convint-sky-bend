import uuid
from operator import attrgetter
from typing import Any

from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from taggit.managers import TaggableManager

from users.abstracts import TimeStampedModel

User = get_user_model()


def get_populate_from(instance: Any) -> str:
    attrs = [attr.replace("__", ".") for attr in instance.AUTOSLUG_FIELDS]
    attrs_values = [attrgetter(attr)(instance) for attr in attrs]
    attrs_values = [str(value) for value in attrs_values]
    attrs_values = [value.split("+")[0] for value in attrs_values]
    return "-".join(attrs_values)


class Article(TimeStampedModel):

    AUTOSLUG_FIELDS = ["title", "created_at"]

    lookup_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, max_length=255
    )
    slug = AutoSlugField(
        populate_from=get_populate_from,
        unique_with=["title", "created_at"],
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    image = CloudinaryField("post_images", blank=True, null=True)
    body = models.TextField()
    tags = TaggableManager()
    is_hidden = models.BooleanField(default=False)
    favorited = models.BooleanField(default=False)
    favoritesCount = models.IntegerField(
        blank=True, default=0, validators=[MinValueValidator(0)]
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="author", null=True
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
