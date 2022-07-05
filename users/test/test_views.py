from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from users.views import (
    PasswordResetAPIView,
    PasswordResetEmailView,
    UserDetail,
    UserList,
)

fake = Faker()
User = get_user_model()

password_reset_email_view = PasswordResetEmailView.as_view()
password_reset_api_view = PasswordResetAPIView.as_view()
user_detail = UserDetail.as_view()
user_list = UserList.as_view()
fake = Faker()


class TestUserList(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        self.factory = APIRequestFactory()

    def test_get_user_list(self) -> None:
        url = reverse("users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self) -> None:
        url = reverse("users")
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

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
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        self.factory = APIRequestFactory()

    def test_get_user_detail(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail_with_invalid_id(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_with_invalid_id(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": -1})
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": self.user.lookup_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 1)

    def test_delete_user_with_invalid_id(self) -> None:
        url = reverse("user-detail", kwargs={"lookup_id": -1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaswwordResetTest(APITestCase):
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
