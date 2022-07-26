import random
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from articles.models import Article

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args: Any, **kwargs: Any) -> Any:
        fake = Faker()

        for _ in range(1000):
            lookup_id = fake.uuid4()
            title = fake.name()
            Article.objects.create(
                title=title,
                lookup_id=lookup_id,
                author=User.objects.create(
                    username=fake.unique.name(),
                    email=fake.unique.email(),
                    password=fake.unique.password(),
                ),
                description=fake.sentence(),
                body=fake.text(),
                tags=random.choice(
                    [
                        "crime",
                        "fantasy",
                        "technology",
                        "travel",
                        "wild",
                        "fashion",
                        "geograpghy",
                        "romance",
                    ]
                ),
                is_hidden=random.choice([True, False]),
                favorited=random.choice([True, False]),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
