# # from urllib import response

# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase

# # from django.urls import reverse
# from faker import Faker

# # from ..serializers import UserSerializer

# # from rest_framework import status

# # from ..models import Profile

# fake = Faker()
# User = get_user_model()


# client = Client()


# class GetAllUsers(TestCase):
#     def setUp(self) -> None:
#         User.objects.create(
#             id=fake.id,
#             username=fake.username,
#             email=fake.email,
#             password=fake.password,
#         )
#         User.objects.create(
#             id=fake.id,
#             username=fake.username,
#             email=fake.email,
#             password=fake.password,
#         )
#         User.objects.create(
#             id=fake.id,
#             username=fake.username,
#             email=fake.email,
#             password=fake.password,
#         )
#         User.objects.create(
#             id=fake.id,
#             username=fake.username,
#             email=fake.email,
#             password=fake.password,
#         )

#     # def get_all_users(self) -> None:
#     #     response = client.get(reverse("users"))
#     #     users = User.objects.all()
#     #     serializer = UserSerializer(users, many=True)
#     #     self.assertEqual(response.data, serializer.data)
#     #     self.assertEqual(response.status_code, 200)

#     # def get_user_by_id(self) -> None:
#     #     response = client.get(reverse("user-detail", kwargs={"pk": self.id}))
#     #     user = User.objects.filter(id=id)
#     #     serializer = UserSerializer(user, many=False)
#     #     self.assertEqual(response.data, serializer.data)
#     #     self.assertEqual(response.status_code, 200)
