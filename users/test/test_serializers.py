from typing import Any

from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework.test import APITestCase

from users.models import Profile
from users.serializers import ProfileSerializer

User = get_user_model()
fake = Faker()


class ProfileTest(APITestCase):
    user: Any
    profile: Any
    serializer_data: dict

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )

        cls.profile = Profile.objects.create(user=cls.user)

        cls.serializer_data = {"bio": "keep at it"}

    def test_profile_update(self) -> None:
        self.serializer_data["bio"] = "try again"

        serializer = ProfileSerializer(
            data=self.serializer_data, instance=self.profile, partial=True
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(
            serializer.data.get("bio"), self.serializer_data.get("bio")
        )
