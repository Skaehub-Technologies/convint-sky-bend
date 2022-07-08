import json
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from users.views import PasswordResetAPIView, PasswordResetEmailView

fake = Faker()
User = get_user_model()
password_reset_email_view = PasswordResetEmailView.as_view()
password_reset_api_view = PasswordResetAPIView.as_view()


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
        url = reverse("user-follow", kwargs={"pk": self.user_one.id})
        response = self.client.post(
            url, kwargs={"pk": self.user_one.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_unfollow(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_one.id})
        response = self.client.delete(
            url, kwargs={"pk": self.user_one.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_follow(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_one.id})
        response = self.client.post(
            url,
            kwargs={"pk": self.user_one.id},
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, text=self.user_one.username)

    def test_authorized_user_unfollow(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_one.id})
        response = self.client.delete(
            url,
            kwargs={"pk": self.user_one.id},
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_get_followers(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_one.id})
        response = self.client.get(
            url,
            kwargs={"pk": self.user_one.id},
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_follow_self(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_two.id})
        response = self.client.post(
            url,
            kwargs={"pk": self.user_two.id},
            format="json",
            **self.bearer_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaisesMessage(PermissionDenied, "failed to reset password")

    def test_user_cannot_follow_same_user(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.user_two.id})

        self.client.post(
            url,
            kwargs={"pk": self.user_two.id},
            format="json",
            **self.bearer_token,
        )
        response = self.client.post(
            url,
            kwargs={"pk": self.user_two.id},
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
        self.factory = APIRequestFactory()

    def test_password_reset_request(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": fake.email()}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_email(self) -> None:
        url = reverse("reset-password-request")

        request = self.factory.post(
            url, {"email": self.user.email}, format="json"
        )
        response = password_reset_email_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        self.assertEqual(
            response.data,
            {"message": "check your email for password reset link"},
        )

    def test_password_reset_no_email(self) -> None:
        url = reverse("reset-password-request")
        request = self.factory.post(url, format="json")
        response = password_reset_email_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_newpassword(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        request = self.factory.patch(
            url, data={"password": "new_password"}, format="json"
        )
        response = password_reset_api_view(
            request,
            data={"password": "new_password"},
            uidb64=uidb64,
            token=token,
        )
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "password changed successfully"}
        )

    def test_password_reset_wrong_token(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        request = self.factory.patch(
            url, data={"password": "new_password"}, format="json"
        )
        response = password_reset_api_view(
            request,
            data={"password": "new_password"},
            uidb64=uidb64,
            token=f"{token}X",
        )
        response.render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"detail": "failed to reset password"})

    def test_password_reset_verify_wrong_uidb64(self) -> None:
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": token}
        )
        request = self.factory.patch(
            url, data={"password": "new_password"}, format="json"
        )
        response = password_reset_api_view(
            request,
            data={"password": "new_password"},
            uidb64=f"{uidb64}X",
            token=token,
        )
        response.render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"detail": "failed to reset password"})
