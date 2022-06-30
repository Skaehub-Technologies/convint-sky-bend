from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from users.views import PasswordResetAPIView, PasswordResetEmailView

User = get_user_model()
password_reset_email_view = PasswordResetEmailView.as_view()
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

    def test_password_reset_verify_wrong_token(self) -> None:
        url = reverse("reset-password", kwargs={"uidb64": None, "token": None})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_verify_wrong_uidb64(self) -> None:
        url = reverse("reset-password", kwargs={"uidb64": None, "token": None})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_email(self) -> None:
        url = reverse("reset-password-request")
        print(url)
        factory = APIRequestFactory()
        request = factory.post(
            url, {"email": self.casper.email}, format="json"
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
        factory = APIRequestFactory()
        request = factory.post(url, {"id": self.casper.id})
        response = password_reset_email_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_wrong_token(self) -> None:
        factory = APIRequestFactory()
        uidb64 = urlsafe_base64_encode(smart_bytes(self.casper.id))
        url = reverse(
            "reset-password", kwargs={"uidb64": uidb64, "token": None}
        )
        request = factory.patch(url)
        response = password_reset_api_view(request, uidb64=uidb64, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
