from django.test import TestCase
from faker import Faker

from articles.models import Article, get_populate_from


class TestArticleModel(TestCase):
    def setUp(self) -> None:
        self.fake = Faker()
        self.data = {
            "title": self.fake.name(),
            "description": self.fake.text(),
            "body": self.fake.text(),
            "image": self.fake.image_url(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }

    def sample_slug(self, str: str) -> str:
        special_chars = "!@#$%^&*()_+{}|:<>?[];'./,`~"
        for char in special_chars:
            str = str.replace(char, "")
        return "-".join(str.split())

    def test_create_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(article.title, self.data["title"])
        self.assertEqual(article.description, self.data["description"])
        self.assertEqual(article.body, self.data["body"])
        self.assertEqual(article.image, self.data["image"])
        self.assertEqual(article.is_hidden, self.data["is_hidden"])
        self.assertEqual(article.favorited, self.data["favorited"])
        self.assertEqual(article.favoritesCount, self.data["favoritesCount"])

    def test_delete_article(self) -> None:
        article = Article.objects.create(**self.data)
        article.delete()
        self.assertEqual(Article.objects.count(), 0)

    def test_str_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(str(article), article.title)

    def test_slug_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(
            article.slug, self.sample_slug(get_populate_from(article).lower())
        )
