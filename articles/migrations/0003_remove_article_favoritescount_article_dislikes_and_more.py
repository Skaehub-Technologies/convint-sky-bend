# Generated by Django 4.0.5 on 2022-07-29 06:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("articles", "0002_alter_article_slug"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="favoritesCount",
        ),
        migrations.AddField(
            model_name="article",
            name="dislikes",
            field=models.ManyToManyField(
                blank=True,
                related_name="dislikes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="likes",
            field=models.ManyToManyField(
                blank=True, related_name="likes", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
