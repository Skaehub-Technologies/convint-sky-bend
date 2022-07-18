import json
from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from articles.models import Article
from articles.test.mocks import sample_image

fake = Faker()
User = get_user_model()


class TestArticleViews(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.password = fake.password()
        self.user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=self.password
        )
        self.article = Article.objects.create(
            title=fake.name(),
            description=fake.text(),
            body=fake.text(),
            image=sample_image(),
            is_hidden=False,
            favorited=False,
            favoritesCount=0,
            author=self.user,
        )

    @property
    def bearer_token(self) -> Any:
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={"email": self.user.email, "password": self.password},
            format="json",
        )
        token = json.loads(response.content).get("access")  # type: ignore[attr-defined]
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    @patch(
        "cloudinary.uploader.upload_resource", return_value=fake.image_url()
    )
    def test_create_article(self, upload_resource: None) -> None:
        data = {
            "title": fake.texts(nb_texts=2),
            "description": fake.paragraph(nb_sentences=3),
            "body": fake.paragraph(nb_sentences=20),
            "image": sample_image(),
            "is_hidden": False,
            "tags": f'["{fake.word()}", "{fake.word()}"]',
            "favorited": False,
            "favoritesCount": 0,
        }

        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertTrue(upload_resource.called)  # type: ignore[attr-defined]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)

    def test_create_article_without_title(self) -> None:
        data = {
            "description": fake.text(),
            "body": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Article.objects.count(), 1)

    def test_create_article_without_tags(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "body": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Article.objects.count(), 1)

    def test_create_article_without_body(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Article.objects.count(), 1)

    def test_create_article_without_authentication(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "body": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Article.objects.count(), 1)

    def test_create_article_with_invalid_image(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "body": fake.text(),
            "image": "invalid_image",
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Article.objects.count(), 1)

    def test_get_articles(self) -> None:
        response = self.client.get(reverse("articles"), **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # type: ignore[attr-defined]
        json_response = json.loads(response.content)  # type: ignore[attr-defined]
        self.assertEqual(self.article.body, json_response[0].get("body"))

    def test_get_article(self) -> None:
        response = self.client.get(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("body"), self.article.body)  # type: ignore[attr-defined]

    def test_get_article_with_invalid_slug(self) -> None:
        response = self.client.get(
            reverse("article-detail", kwargs={"slug": "invalid_slug"}),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_article_without_authentication(self) -> None:
        response = self.client.get(
            reverse("article-detail", kwargs={"slug": self.article.slug})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_article(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "body": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.patch(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("body"), data.get("body"))  # type: ignore[attr-defined]

    def test_update_article_without_authentication(self) -> None:
        data = {
            "title": fake.text(),
            "description": fake.text(),
            "body": fake.text(),
            "image": sample_image(),
            "is_hidden": False,
            "favorited": False,
            "favoritesCount": 0,
        }
        response = self.client.patch(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_article(self) -> None:
        response = self.client.delete(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)

    def test_delete_article_without_authentication(self) -> None:
        response = self.client.delete(
            reverse("article-detail", kwargs={"slug": self.article.slug})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Article.objects.count(), 1)
