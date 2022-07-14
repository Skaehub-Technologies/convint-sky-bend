# Generated by Django 4.0.5 on 2022-07-07 07:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_userfollowing_follower"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfollowing",
            name="follower",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="following",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
