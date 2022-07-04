import json
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from users.views import PasswordResetAPIView, PasswordResetEmailView

fake = Faker()
User = get_user_model()

password_reset_email_view = PasswordResetEmailView.as_view()
password_reset_api_view = PasswordResetAPIView.as_view()
fake = Faker()


@pytest.mark.django_db
def test_user_view(client: Any) -> None:
    url = reverse("users")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_detail(client: Any, django_user_model: Any) -> None:
    password = fake.password()
    email = fake.email()
    user = django_user_model.objects.create(password=password, email=email)
    url = reverse("user-detail", kwargs={"pk": user.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_detail_not_found(client: Any, django_user_model: Any) -> None:
    url = reverse("user-detail", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_user_not_user(client: Any, django_user_model: Any) -> None:
    password = fake.password()
    email = fake.email()
    user = django_user_model.objects.create(password=password, email=email)
    url = reverse("user-detail", kwargs={"pk": user.pk})
    response = client.delete(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_user_not_found(client: Any, django_user_model: Any) -> None:
    url = reverse("user-detail", kwargs={"pk": 1})
    response = client.delete(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_user(client: Any, django_user_model: Any) -> None:
    password = fake.password()
    email = fake.email()
    user = django_user_model.objects.create(password=password, email=email)
    url = reverse("user-detail", kwargs={"pk": user.pk})
    response = client.delete(url)
    assert response.status_code == 401
    assert django_user_model.objects.filter(pk=user.pk).count() == 1


@pytest.mark.django_db
def test_user_register(client: Any) -> None:
    test_data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }

    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(test_data),
        content_type="application/json",
    )
    # data = response.json.get("user")
    assert response.status_code == 201
    # assert data.get("email") == test_data.get("email")
    # assert data.get("username") == test_data.get("username")


@pytest.mark.django_db
def test_user_register_duplicate_email(client: Any) -> None:
    test_data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }

    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(test_data),
        content_type="application/json",
    )
    assert response.status_code == 201
    response = client.post(
        url,
        data=json.dumps(test_data),
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_user_login_fail(client: Any) -> None:
    test_data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }

    url = reverse("login")
    response = client.post(
        url,
        data=json.dumps(test_data),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_login(client: Any) -> None:
    data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }
    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 201
    url = reverse("login")
    response = client.post(
        url,
        data=json.dumps(
            {
                "email": data["email"],
                "password": data["password"],
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_update_user_by_id(client: Any) -> None:
    data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }

    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 201

    updated_data = {
        "email": fake.email(),
    }
    url = reverse("user-update", kwargs={"pk": 1})
    response = client.put(
        url,
        data=json.dumps(updated_data),
        content_type="application/json",
    )


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
