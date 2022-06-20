from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from faker import Faker

fake = Faker()
User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.assertNotEqual(user.email, fake.email())
        
    
    def test_password_exception_raised(self):
           with self.assertRaises(ValueError):
            User.objects.create_user(
                username=fake.name(),
                email = fake.email(),
                password = ''
            )

    def test_Email_exception_raised(self):
           with self.assertRaises(ValueError):
            User.objects.create_user(
                username=fake.name(),
                email = '',
                password = fake.password()
            )
       
    def test_is_editor(self):
        user = User.objects.create_editor(
        email = fake.email(), password = fake.password(), is_editor =False
        )
        self.assertTrue(user.is_editor)


    def test_superuser(self):
        super_user = User.objects.create_superuser(email= fake.email(), password=fake.password())
        self.assertNotEqual(super_user.email, fake.email())

    def test_superuser_password_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
            username=fake.name(), email=fake.email(), password=""
        )

    def test_superuser_email_error(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
            username='', email='', password=fake.password()
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
        is_superuser=True,)
        self.assertTrue = (user.is_superuser)
      