# type: ignore [attr-defined]

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from articles.models import Article, Comment
from articles.tests.mocks import sample_data, sample_image
from users.models import Profile

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
        count = Article.objects.count()
        self.assertEqual(response.data.get("count"), count)
        json_response = response.json().get("results")
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

    def test_get_article_with_invalid_slug_fail(self) -> None:
        url = reverse("article-detail", kwargs={"slug": self.article.slug})
        response = self.client.get(
            url,
            **self.bearer_token,
        )
        data = {"slug": "updated-slug"}
        response = self.client.patch(
            url,
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
            **self.bearer_token,
        )
        response = self.client.get(
            url,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestCommentViews(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.password = fake.password()
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=cls.password
        )
        cls.profile = Profile.objects.create(user=cls.user)
        cls.article = Article.objects.create(
            title=fake.text(),
            body=fake.text(),
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            author=cls.profile, article=cls.article, body=fake.text()
        )
        cls.data = {
            "body": fake.text(),
            "article": cls.article,
            "author": cls.profile,
        }

    @property
    def bearer_token(self) -> dict:
        """
        Returns a bearer token for the client
        """
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={"email": self.user.email, "password": self.password},
            format="json",
        )
        token = json.loads(response.content).get("access")
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_create_comment(
        self,
    ) -> None:
        """
        Test that a comment can be created
        """
        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(self.data.get("body")), self.data.get("body"))

    def test_create_comment_without_authentication(
        self,
    ) -> None:
        """
        Test that a comment cannot be created without authentication
        """
        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )

    def test_get_all_comments(
        self,
    ) -> None:
        """
        Test that all comments can be retrieved
        """
        response = self.client.get(
            reverse(
                "comments",
                kwargs={
                    "slug": self.article.slug,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.body, str)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comments fetched successfully",
        )

    def test_get_comment(
        self,
    ) -> None:
        """
        Test that a comment can be retrieved with a valid lookup_id
        """
        response = self.client.get(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.body, str)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comment fetched successfully",
        )

    def test_get_comment_without_authentication(
        self,
    ) -> None:
        """
        Test that a comment can be retrieved without authentication
        """
        response = self.client.get(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.body, str)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comment fetched successfully",
        )

    def test_get_comment_with_invalid_lookup_id(
        self,
    ) -> None:
        """
        Test that a comment cannot be retrieved with an invalid lookup_id
        """
        with self.assertRaises(ValidationError):
            self.client.get(
                reverse(
                    "comment-detail",
                    kwargs={
                        "slug": self.article.slug,
                        "lookup_id": "invalid-id",
                    },
                ),
            )

    def test_update_comment(
        self,
    ) -> None:
        """
        Test that a comment can be updated
        """
        data = {"body": fake.text()}
        response = self.client.patch(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
            data=data,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comment updated successfully",
        )

    def test_update_comment_without_authentication(
        self,
    ) -> None:
        """
        Test that a comment cannot be updated without authentication
        """
        data = {"body": fake.text()}
        response = self.client.patch(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )

    def test_delete_comment(
        self,
    ) -> None:
        """
        Test that a comment can be deleted
        """
        response = self.client.delete(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_without_authentication(
        self,
    ) -> None:
        """
        Test that a comment cannot be deleted without authentication
        """
        response = self.client.delete(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )


class TestHighlightCommentViews(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.password = fake.password()
        cls.client = APIClient()
        cls.user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=cls.password
        )
        cls.profile = Profile.objects.create(user=cls.user)
        cls.article = Article.objects.create(
            title=fake.text(),
            body=fake.text(),
            author=cls.user,
        )

        start = fake.pyint(min_value=1, max_value=len(cls.article.body))
        end = fake.pyint(min_value=start, max_value=len(cls.article.body))
        cls.comment = Comment.objects.create(
            author=cls.profile,
            article=cls.article,
            body=fake.text(),
            highlight_end=end,
            highlight_start=start,
        )

        highlight_start = fake.pyint(
            min_value=1, max_value=len(cls.article.body)
        )
        highlight_end = fake.pyint(
            min_value=highlight_start, max_value=len(cls.article.body)
        )
        cls.data = {
            "body": fake.text(),
            "highlight_start": highlight_start,
            "highlight_end": highlight_end,
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

    def test_create_highlight_comment(
        self,
    ) -> None:
        """
        Test that a text can be highlighted and commented on an article
        """

        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
            **self.bearer_token,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comment added successfully",
        )

    def test_highlight_comment_create_without_authentication(
        self,
    ) -> None:
        """
        Test that a comment cannot be created without authentication
        """
        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Authentication credentials were not provided.",
        )

    def test_highlight_comment_create_with_invalid_article(
        self,
    ) -> None:
        """
        Test that a comment cannot be created with an invalid article
        """
        response = self.client.post(
            reverse("comments", kwargs={"slug": "am-here-to-see-the-error"}),
            data=self.data,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            json.loads(response.content).get("detail"),
            "Not found.",
        )

    def test_invalid_highlight_start(
        self,
    ) -> None:
        """
        Test that a comment cannot be created with an invalid highlight start
        """
        self.data["highlight_start"] = fake.pyint(
            min_value=len(self.article.body) + 1
        )
        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)[0],
            "Index must not exceed article length.",
        )

    def test_highlight_comment_create_with_invalid_highlight_end(
        self,
    ) -> None:
        """
        Test that a comment cannot be created with an invalid highlight end
        """
        self.data["highlight_end"] = fake.pyint(
            min_value=len(self.article.body) + 1
        )
        response = self.client.post(
            reverse("comments", kwargs={"slug": self.article.slug}),
            data=self.data,
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_highlight_comments(
        self,
    ) -> None:
        """
        Test that a comment can be retrieved with a valid article slug
        """
        response = self.client.get(
            reverse("comments", kwargs={"slug": self.article.slug})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.body, str)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comments fetched successfully",
        )

    def test_detail_highlight_comment(
        self,
    ) -> None:
        """
        Test that a comment can be retrieved with a valid comment lookup_id
        """

        response = self.client.get(
            reverse(
                "comment-detail",
                kwargs={
                    "slug": self.article.slug,
                    "lookup_id": self.comment.lookup_id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.body, str)
        self.assertEqual(
            json.loads(response.content).get("message"),
            "Comment fetched successfully",
        )
