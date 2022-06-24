from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from ..views import UserFollowView

User = get_user_model()
follow_view = UserFollowView.as_view()


class TestFollowingView(APITestCase):
    def setUp(self) -> None:
        self.casper = User.objects.create(
            username="Casper", email="casper@mail.com", password="password"
        )
        self.muffin = User.objects.create(
            username="Muffin", email="Muffin@mail.com", password="password"
        )
        self.rambo = User.objects.create(
            username="Rambo", email="Rambo@mail.com", password="password"
        )
        self.ricky = User.objects.create(
            username="Ricky", email="Ricky@mail.com", password="password"
        )

    def test_unauthorized_user_follow(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.casper.id})
        response = self.client.post(
            url, kwargs={"pk": self.casper.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_unfollow(self) -> None:
        url = reverse("user-follow", kwargs={"pk": self.casper.id})
        response = self.client.delete(
            url, kwargs={"pk": self.casper.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_follow(self) -> None:
        factory = APIRequestFactory()
        url = reverse("user-follow", kwargs={"pk": self.casper.id})
        request = factory.post(url)
        force_authenticate(request, user=self.muffin)
        response = follow_view(request, pk=self.casper.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        self.assertContains(response, text="Muffin")

    def test_authorized_user_unfollow(self) -> None:
        factory = APIRequestFactory()
        url = reverse("user-follow", kwargs={"pk": self.casper.id})
        request = factory.delete(url)
        force_authenticate(request, user=self.muffin)
        response = follow_view(request, pk=self.casper.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_get_followers(self) -> None:
        factory = APIRequestFactory()
        url = reverse("user-follow", kwargs={"pk": self.casper.id})
        request = factory.get(url)
        force_authenticate(request, user=self.muffin)
        response = follow_view(request, pk=self.casper.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
