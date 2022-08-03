import uuid
from typing import Any

from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from taggit.managers import TaggableManager

from users.abstracts import TimeStampedModel

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
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(
        User, related_name="dislikes", blank=True
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
