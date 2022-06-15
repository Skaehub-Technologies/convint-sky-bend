from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client


Member = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = Member.objects.create_user(
            email="test@test.com", password="hello"
        )
        user.save()
        self.assertEqual(user.email, "test@test.com")
    
    def test_password_exception_raised(self):
           with self.assertRaises(ValueError):
            Member.objects.create_user(
                username='me',
                email = 'me@test.com',
                password = ''
            )

    def test_Email_exception_raised(self):
           with self.assertRaises(ValueError):
            Member.objects.create_user(
                username='me',
                email = '',
                password = '123345'
            )
            
        
    def test_create_editor(self):
        editor = Member.objects.create_editor(
            email = 'example@ex.com', password = '123456'
        )
        self.assertEqual(editor.email, 'example@ex.com')

    def test_superuser(self):
        super_user = Member.objects.create_superuser(email= 'test@test.com', password='1234')
        self.assertEqual(super_user.email, 'test@test.com')

    def test_superuser_password_error(self) -> None:
        with self.assertRaises(ValueError):
            Member.objects.create_superuser(
            username="me", email="mesuperuser@test.com", password=""
        )

    def test_superuser_email_error(self) -> None:
        with self.assertRaises(ValueError):
            Member.objects.create_superuser(
            username="me", email="", password="12345"
        )

    def test_superuser_staff_error(self) -> None:
        with self.assertRaises(ValueError):
            Member.objects.create_superuser(
            email="teststaff@test.com",
            password="12345",
            is_staff=False,
        )

    def test_superuser_error(self) -> None:
        with self.assertRaises(ValueError):
            Member.objects.create_superuser(
            email="mesuperuser@test.com",
            password='12345',
            is_superuser=False,
    )


class TestUser(TestCase):
    def test_user(self):
        self.user = Member.objects.create(username= 'me', email = 'me@test.com', password= '12345')
        self.user_check = Member.objects.filter(email__iexact='me@test.com')
        self.user_exist = self.user_check.exists()
        self.assertEqual(self.user_exist,1)
        # self.assertRegex(user.email, str('@'))
        self.assertIsInstance(self.user.email, str)
      
   
    # def test_user(self):
    #     c = Client()
    #     user_email = c.post('/login/', {'username': 'me', 'email': 'me@test.com'})
    #     self.assertIsInstance(user_email, str)