# Generated by Django 4.0.5 on 2022-08-04 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0004_remove_article_favorited"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="reading_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
