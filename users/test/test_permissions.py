import pytest
from django.contrib.auth import get_user_model

from .mocks import test_user

User = get_user_model()


@pytest.mark.django_db
def test_can_registerbutcant_get_list() -> None:
    user = User.objects.create_user(**test_user)
    assert user.is_authenticated
    assert user.is_active
    assert user.email == test_user["email"]
    assert user.username == test_user["username"]
