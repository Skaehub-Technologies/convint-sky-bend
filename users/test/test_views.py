import json
from typing import Any

import pytest
from django.urls import reverse
from faker import Faker

fake = Faker()


@pytest.mark.django_db
def test_user_view(client: Any) -> None:
    url = reverse("users")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_detail(client: Any, django_user_model: Any) -> None:
    password = fake.password()
    email = fake.email()
    user = django_user_model.objects.create(password=password, email=email)
    url = reverse("user-detail", kwargs={"pk": user.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_register(client: Any) -> None:
    test_data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }

    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(test_data),
        content_type="application/json",
    )
    # data = response.json.get("user")
    assert response.status_code == 201
    # assert data.get("email") == test_data.get("email")
    # assert data.get("username") == test_data.get("username")


@pytest.mark.django_db
def test_login(client: Any) -> None:
    data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }
    url = reverse("register")
    response = client.post(
        url,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 201
    url = reverse("login")
    response = client.post(
        url,
        data=json.dumps(
            {
                "email": data["email"],
                "password": data["password"],
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
