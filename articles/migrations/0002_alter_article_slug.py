# Generated by Django 4.0.5 on 2022-07-19 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="slug",
            field=models.SlugField(
                blank=True, max_length=255, null=True, unique=True
            ),
        ),
    ]
