from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework.test import APIClient, APITestCase

from users.serializers import ProfileSerializer

User = get_user_model()
fake = Faker()


class ProfileTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )

        self.client = APIClient()

        self.serializer_data = {"bio": "keep at it"}

    def test_serializers_has_expected_fields(self) -> None:
        data = self.serializer_data
        self.assertEqual(set(data.values()), set(["keep at it"]))

    def test_profile_update(self) -> None:
        self.serializer_data["bio"] = "try again"

        serializer = ProfileSerializer(data=self.serializer_data)

        self.assertTrue(serializer.is_valid())
        self.assertNotEqual(set(serializer.errors), set(["bio"]))
