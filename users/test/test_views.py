import json
from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from users.models import Profile

from .mocks import test_image, test_user, test_user_2

fake = Faker()
User = get_user_model()


class TestUserList(APITestCase):
    user: Any

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user)

    @property
    def bearer_token(self) -> str:
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={
                "email": test_user["email"],
                "password": test_user["password"],
            },
            format="json",
        )
        return response.data.get("access")  # type: ignore[no-any-return,attr-defined]

    def test_create_user(self) -> None:
        url = reverse("users")
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        outbox = len(mail.outbox)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), outbox + 1)

    def test_user_login(self) -> None:
        url = reverse("login")
        response = self.client.post(
            url,
            data={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_list(self) -> None:

        url = reverse("users")
        self.client.credentials(  # type: ignore[attr-defined]
            HTTP_AUTHORIZATION=f"Bearer {self.bearer_token}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_with_existing_email(self) -> None:
        url = reverse("users")
        data = {
            "username": fake.user_name(),
            "email": self.user.email,
            "password": fake.password(),
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserDetail(APITestCase):
    user: Any

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user_2)

    @property
    def bearer_token(self) -> str:
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={
                "email": test_user_2["email"],
                "password": test_user_2["password"],
            },
            format="json",
        )
        return response.data.get("access")  # type: ignore[no-any-return,attr-defined]

    def test_get_user_detail(self) -> Any:
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        self.client.credentials(  # type: ignore[attr-defined]
            HTTP_AUTHORIZATION=f"Bearer {self.bearer_token}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail_with_invalid_id(self) -> None:
        self.client.credentials(  # type: ignore[attr-defined]
            HTTP_AUTHORIZATION=f"Bearer {self.bearer_token}"
        )
        url = reverse("user-detail", kwargs={"lookup_id": -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self) -> None:
        self.client.credentials(  # type: ignore[attr-defined]
            HTTP_AUTHORIZATION=f"Bearer {self.bearer_token}"
        )
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        username = fake.user_name()
        response = self.client.patch(url, data={"username": username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), username)  # type: ignore[attr-defined]

    def test_delete_user(self) -> None:
        self.client.credentials(  # type: ignore[attr-defined]
            HTTP_AUTHORIZATION=f"Bearer {self.bearer_token}"
        )
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestVerifyEmailView(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(**test_user)
        self.client = APIClient()

    def test_verify_email(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.lookup_id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "verify-email", kwargs={"uidb64": uidb64, "token": token}
        )
        response = self.client.post(
            url, data={"uidb64": uidb64, "token": token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Your email is verified")  # type: ignore[attr-defined]

    def test_verify_email_with_invalid_uidb64(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(-1))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "verify-email", kwargs={"uidb64": uidb64, "token": token}
        )
        response = self.client.post(
            url, data={"uidb64": uidb64, "token": token}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("failed to verify", str(response.data))  # type: ignore[attr-defined]


class ProfileTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(**test_user)

        self.client = APIClient()

    @patch(
        "cloudinary.uploader.upload_resource", return_value=fake.image_url()
    )
    def test_profile_update(self, upload_resource: None) -> None:
        Profile.objects.create(user=self.user)
        login_url = reverse("login")
        res = self.client.post(
            login_url,
            data={
                "email": test_user["email"],
                "password": test_user["password"],
            },
            format="json",
        )
        data = {"bio": "test validity", "image": test_image}
        url = reverse("profile", kwargs={"lookup_id": self.user.lookup_id})
        self.client.defaults[
            "HTTP_AUTHORIZATION"
        ] = f"Bearer {res.data['access']}"  # type: ignore[attr-defined]
        response = self.client.patch(
            url,
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            enctype="multipart/form-data",
        )

        self.assertTrue(upload_resource.called)  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestFollowingView(APITestCase):
    def setUp(self) -> None:
        self.password = fake.password()
        self.user_one = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=self.password
        )
        self.user_two = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=self.password
        )
        self.client = APIClient()

    @property
    def bearer_token(self) -> Any:
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            data={"email": self.user_two.email, "password": self.password},
            format="json",
        )
        token = json.loads(response.content).get("access")  # type: ignore[attr-defined]
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_unauthorized_user_follow(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_unfollow(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_follow(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
        )
        response = self.client.post(
            url,
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, text=self.user_one.username)

    def test_authorized_user_unfollow(self) -> None:
        self.client.post(
            reverse(
                "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
            ),
            format="json",
            **self.bearer_token,
        )
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
        )
        response = self.client.delete(
            url,
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_get_followers(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_one.lookup_id}
        )
        response = self.client.get(
            url,
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_follow_self(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_two.lookup_id}
        )
        response = self.client.post(
            url,
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaisesMessage(PermissionDenied, "failed to reset password")

    def test_user_cannot_follow_same_user(self) -> None:
        url = reverse(
            "user-follow", kwargs={"lookup_id": self.user_two.lookup_id}
        )

        self.client.post(
            url,
            format="json",
            **self.bearer_token,
        )
        response = self.client.post(
            url,
            format="json",
            **self.bearer_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertRaisesMessage(
            PermissionDenied, "you are already following this user"
        )


class PaswwordResetTest(APITestCase):
    """test password reset email view"""

    def setUp(self) -> None:
        self.user = User.objects.create(
            username=fake.name(), email=fake.email(), password=fake.password()
        )
        self.client = APIClient()

    def test_password_reset_request(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": fake.email()}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_email(self) -> None:
        url = reverse("reset-password-request")

        response = self.client.post(
            url, {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,  # type: ignore[attr-defined]
            {"message": "check your email for password reset link"},
        )

    def test_password_reset_no_email(self) -> None:
        url = reverse("reset-password-request")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_newpassword(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.lookup_id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        response = self.client.patch(
            url, data={"password": fake.password()}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "password changed successfully"}  # type: ignore[attr-defined]
        )

    def test_password_reset_wrong_token(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        response = self.client.patch(
            url, data={"password": fake.password()}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("failed to reset password", response.data["detail"])  # type: ignore[attr-defined]

    def test_password_reset_verify_wrong_uidb64(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes("cetrt5t56"))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        response = self.client.patch(
            url, data={"password": fake.password()}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("failed to reset password", response.data["detail"])  # type: ignore[attr-defined]
