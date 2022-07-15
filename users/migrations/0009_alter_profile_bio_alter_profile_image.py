# Generated by Django 4.0.5 on 2022-07-15 12:57

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_alter_user_lookup_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="bio",
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="profile_pics",
            ),
        ),
    ]
