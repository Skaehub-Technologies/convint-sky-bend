from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from users.views import ProfileView

User = get_user_model()
profile_view = ProfileView.as_view()
faker = Faker()


class ProfileTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username=faker.name(),
            email=faker.email(),
            password=faker.password(),
        )

        self.factory = APIRequestFactory()

    def test_user_profile_setup(self) -> None:
        url = reverse("profile")
        data = {"bio": "Win self"}

        request = self.factory.post(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = profile_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        self.assertEqual(response.data["bio"], "Win self")
