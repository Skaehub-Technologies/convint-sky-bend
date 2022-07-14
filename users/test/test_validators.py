import pytest

from users.validators import (
    validate_password_digit,
    validate_password_lowercase,
    validate_password_symbol,
    validate_password_uppercase,
)


@pytest.mark.parametrize("value", ["123456789", "1234567890"])
def test_validate_password_digit(value: str) -> None:
    assert validate_password_digit(value) == value


def test_validate_password_uppercase() -> None:
    assert validate_password_uppercase("123456789") == "123456789"


def test_validate_password_symbol() -> None:
    assert validate_password_symbol("123456789") == "123456789"


def test_validate_password_lowercase() -> None:
    assert validate_password_lowercase("123456789") == "123456789"
