from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

from users.models import Profile

fake = Faker()
User = get_user_model()


class UserModelTest(TestCase):
    user: Any

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        data = {
            "username": fake.name(),
            "email": fake.email(),
            "password": fake.password(),
        }

        cls.user = User.objects.create_user(**data)

    def test_create_user(self) -> None:
        data = {
            "username": fake.name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        user = User.objects.create_user(**data)
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.username, data["username"])

    def test_password_exception_raised(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username=fake.name(), email=fake.email(), password=""
            )

    def test_Email_exception_raised(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username=fake.name(), email="", password=fake.password()
            )

    def test_is_editor(self) -> None:
        user = User.objects.create_editor(
            email=fake.email(), password=fake.password(), is_editor=False
        )
        self.assertTrue(user.is_editor)

    def test_superuser(self) -> None:
        super_user = User.objects.create_superuser(
            email=fake.email(), password=fake.password()
        )
        self.assertNotEqual(super_user.email, fake.email())

    def test_superuser_password_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username=fake.name(), email=fake.email(), password=""
            )

    def test_superuser_email_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="", email="", password=fake.password()
            )

    def test_superuser_staff_error(self) -> None:
        user = User.objects.create_superuser(
            email=fake.email(),
            password=fake.password(),
            is_staff=True,
        )
        self.assertTrue(user.is_staff)

    def test_superuser_error(self) -> None:
        user = User.objects.create_superuser(
            email=fake.email(),
            password=fake.password(),
            is_superuser=True,
        )
        self.assertTrue == user.is_superuser

    def test_user_representation_is_email(self) -> None:
        user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password=fake.password()
        )
        self.assertEqual(str(user), user.email)

    def test_user_profile(self) -> None:
        profile = Profile.objects.create(
            user=self.user,
            bio="try again",
        )

        self.assertEqual(str(profile), self.user.username)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
