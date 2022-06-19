from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PaswwordResetTest(APITestCase):
    def test_password_reset_request(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": "kidbrion7@gmail.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_verify(self) -> None:
        url = reverse("reset-password-request")
        data = {"email": "kidbrion7@gmail.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
