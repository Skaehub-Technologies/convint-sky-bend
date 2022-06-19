from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

fake = Faker()
User = get_user_model()

<<<<<<< HEAD

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
=======

class UserModelTest(TestCase):
    def test_create_user(self) -> None:
        user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.assertNotEqual(user.email, fake.email())

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
        with self.assertRaises(ValueError):
            User.objects.create_editor(
                email=fake.email(), password=fake.password(), is_editor=True
            )

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
                username="", email=fake.email(), password=fake.password()
            )

    def test_superuser_staff_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=fake.email(),
                password=fake.password(),
                is_staff=False,
            )

    def test_superuser_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=fake.email(),
                password=fake.password(),
                is_superuser=False,
            )


class TestUser(TestCase):
    def test_user(self) -> None:
        self.user = User.objects.create(
            username="me", email="me@test.com", password="12345"
        )
        self.user_check = User.objects.filter(email__iexact="me@test.com")
        self.user_exist = self.user_check.exists()
        self.assertEqual(self.user_exist, 1)
        self.assertIsInstance(self.user.email, str)
>>>>>>> ec4625a (ft(reset-password-via-email): enable users to reset passwords via email)
