# type: ignore [attr-defined]

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from articles.models import Article
from articles.test.mocks import sample_data, sample_image

fake = Faker()
User = get_user_model()


class TestArticleViews(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.password = fake.password()
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=cls.password
        )
        cls.article = Article.objects.create(
            title=fake.name(),
            description=fake.text(),
            body=fake.text(),
            image=sample_image(),
            is_hidden=False,
            favorited=False,
            favoritesCount=0,
            author=cls.user,
        )
        cls.data = {
            "title": fake.texts(nb_texts=2),
            "description": fake.paragraph(nb_sentences=3),
            "body": fake.paragraph(nb_sentences=20),
            "image": sample_image(),
            "is_hidden": False,
            "tags": f'["{fake.word()}", "{fake.word()}"]',
            "favorited": False,
            "favoritesCount": 0,
        }

    @property
    def bearer_token(self) -> dict:
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={"email": self.user.email, "password": self.password},
            format="json",
        )
        token = json.loads(response.content).get("access")
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    @patch(
        "cloudinary.uploader.upload_resource", return_value=fake.image_url()
    )
    def test_create_article(self, upload_resource: None) -> None:
        count = Article.objects.count()
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=self.data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertTrue(upload_resource.called)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), count + 1)

    def test_create_article_without_title(self) -> None:
        data = sample_data()
        data.pop("title")
        count = Article.objects.count()
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.dumps(response.data), '{"title": ["This field is required."]}'
        )
        self.assertEqual(Article.objects.count(), count)

    def test_create_article_without_tags(self) -> None:
        data = sample_data()
        data.pop("tags")

        count = Article.objects.count()
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.dumps(response.data), '{"tags": ["This field is required."]}'
        )
        self.assertEqual(Article.objects.count(), count)

    def test_create_article_without_body(self) -> None:
        data = self.data.copy()
        data.pop("body")
        data["image"] = sample_image()
        count = Article.objects.count()
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.dumps(response.data), '{"body": ["This field is required."]}'
        )
        self.assertEqual(Article.objects.count(), count)

    def test_create_article_without_authentication(self) -> None:
        count = Article.objects.count()
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=self.data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )
        self.assertEqual(Article.objects.count(), count)

    def test_create_article_with_invalid_image(self) -> None:
        data = self.data
        data = {**data, "image": "invalid_image"}
        response = self.client.post(
            reverse("articles"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content).get("image"),
            [
                "The submitted data was not a file. Check the encoding type on the form."
            ],
        )
        self.assertEqual(Article.objects.count(), 1)

    def test_get_articles(self) -> None:
        response = self.client.get(reverse("articles"), **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        json_response = json.loads(response.content)
        self.assertEqual(self.article.body, json_response[0].get("body"))

    def test_get_article(self) -> None:
        response = self.client.get(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.article.body, json.loads(response.content).get("body")
        )

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
        self.assertEqual(
            self.article.body, json.loads(response.content).get("body")
        )

    def test_update_article(self) -> None:
        data = {"title": "Updated title"}
        response = self.client.patch(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), data.get("title"))

    def test_update_article_without_authentication(self) -> None:

        response = self.client.patch(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            data=encode_multipart(data=self.data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )

    def test_delete_article(self) -> None:
        count = Article.objects.count()
        response = self.client.delete(
            reverse("article-detail", kwargs={"slug": self.article.slug}),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), count - 1)

    def test_delete_article_without_authentication(self) -> None:
        count = Article.objects.count()
        response = self.client.delete(
            reverse("article-detail", kwargs={"slug": self.article.slug})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Article.objects.count(), count)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )
