from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.text import slugify
from faker import Faker

from articles.models import Article, Comment

fake = Faker()

User = get_user_model()


class TestArticleModel(TestCase):
    def setUp(self) -> None:
        self.data = {
            "title": fake.name(),
            "description": fake.text(),
            "body": fake.text(),
            "image": fake.image_url(),
            "is_hidden": False,
        }

    def test_create_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(article.title, self.data["title"])
        self.assertEqual(article.description, self.data["description"])
        self.assertEqual(article.body, self.data["body"])
        self.assertEqual(article.image, self.data["image"])
        self.assertEqual(article.is_hidden, self.data["is_hidden"])

    def test_str_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(str(article), article.title)

    def test_slug_article(self) -> None:
        article = Article.objects.create(**self.data)
        self.assertEqual(
            article.slug, slugify(f"{article.title}-{article.lookup_id}")
        )


class TestCommentModel(TestCase):
    def setUp(self) -> None:
        comment_data = {"body": fake.text()}
        signup_data = {
            "username": fake.name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        article = Article.objects.create(**comment_data)
        user = User.objects.create_user(**signup_data)
        self.data = {
            "body": fake.text(max_nb_chars=500),
            "author": user,
            "article": article,
        }

    def test_create_comment(self) -> None:
        comment = Comment.objects.create(**self.data)
        self.assertEqual(comment.body, self.data["body"])

    def test_str_comment(self) -> None:
        comment = Comment.objects.create(**self.data)
        self.assertEqual(str(comment.body), comment.body)
