from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

fake = Faker()
User = get_user_model()


class TestUserModel(TestCase):
    def test_create_user(self) -> None:
        email = fake.email()
        user = User.objects.create_user(email=email, password=fake.password())
        self.assertEqual(user.email, email)

    def test_password_exception_raised(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_user(email=fake.email(), password="")

    def test_Email_exception_raised(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=fake.password())

    def test_is_editor(self) -> None:
        email = fake.email()
        user = User.objects.create_editor(
            email=email, password=fake.password()
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_editor)

    def test_superuser(self) -> None:
        email = fake.email()
        user = User.objects.create_superuser(
            email=email, password=fake.password()
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_superuser_password_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email=fake.email(), password="")

    def test_superuser_email_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="", password=fake.password())

    def test_user_representation_is_email(self) -> None:
        user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.assertEqual(str(user), user.email)
