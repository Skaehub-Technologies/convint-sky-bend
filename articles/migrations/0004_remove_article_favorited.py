# Generated by Django 4.0.5 on 2022-07-29 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "articles",
            "0003_remove_article_favoritescount_article_dislikes_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="favorited",
        ),
    ]