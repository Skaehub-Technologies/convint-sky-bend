from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .mocks import test_user


class TestUserSerializer(APITestCase):
    def setUp(self) -> Any:
        self.user = get_user_model().objects.create_user(**test_user)

    def test_reset_password_request(self) -> None:
        url = reverse("reset-password-request")
        self._extracted_from_test_reset_password_request_3(url)

    def _extracted_from_test_reset_password_request_3(self, url) -> None:  # type: ignore[no-untyped-def]
        data = {"email": test_user["email"]}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
