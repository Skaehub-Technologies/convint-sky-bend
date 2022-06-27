from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from users.views import PasswordResetAPIView, PasswordResetEmail

User = get_user_model()
password_reset_view = PasswordResetEmail.as_view()
password_reset_api_view = PasswordResetAPIView.as_view()


class PaswwordResetTest(APITestCase):
    def setUp(self) -> None:
        self.casper = User.objects.create(
            username="Casper", email="casper@mail.com", password="password"
        )

    def test_password_reset_request(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": "kidbrion7@gmail.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_verify(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": self.casper.email}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_verify_wrong_token(self) -> None:
        url = reverse(
            "reset-password-verify", kwargs={"uidb64": None, "token": None}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_verify_wrong_uidb64(self) -> None:
        url = reverse(
            "reset-password-verify", kwargs={"uidb64": None, "token": None}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_email(self) -> None:
        url = reverse("reset-password-request")
        factory = APIRequestFactory()
        request = factory.post(url, {"email": self.casper.email})
        response = password_reset_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        self.assertEqual(
            response.data,
            {"message": "check your email for password reset link"},
        )

    def test_password_reset_no_email(self) -> None:
        url = reverse("reset-password-request")
        factory = APIRequestFactory()
        request = factory.post(url, {"id": self.casper.id})
        response = password_reset_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset(self) -> None:
        factory = APIRequestFactory()
        uidb64 = urlsafe_base64_encode(smart_bytes(self.casper.id))
        token = PasswordResetTokenGenerator().make_token(self.casper)
        url = reverse(
            "reset-password-verify", kwargs={"uidb64": uidb64, "token": token}
        )
        request = factory.get(url)
        response = password_reset_api_view(request, uidb64=uidb64, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_wrong_token(self) -> None:
        factory = APIRequestFactory()
        uidb64 = urlsafe_base64_encode(smart_bytes(self.casper.id))
        url = reverse(
            "reset-password-verify", kwargs={"uidb64": uidb64, "token": None}
        )
        request = factory.get(url)
        response = password_reset_api_view(request, uidb64=uidb64, token=None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_newpassword(self) -> None:
        factory = APIRequestFactory()
        uidb64 = urlsafe_base64_encode(smart_bytes(self.casper.id))
        token = PasswordResetTokenGenerator().make_token(self.casper)
        url = reverse("reset-password")
        request = factory.patch(
            url, {"uidb64": uidb64, "token": token, "password": "newpassword"}
        )
        response = password_reset_api_view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "password changed successfully"}
        )
