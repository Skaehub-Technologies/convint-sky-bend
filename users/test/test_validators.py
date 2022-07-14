import pytest
from django.core.exceptions import ValidationError

from users.validators import (
    validate_password_digit,
    validate_password_lowercase,
    validate_password_symbol,
    validate_password_uppercase,
)


@pytest.mark.parametrize("value", ["123456789", "1234567890"])
def test_validate_password_digit(value: str) -> None:
    assert validate_password_digit(value) == value
    with pytest.raises(ValidationError):
        validate_password_digit("TYU@wdhdh")


def test_validate_password_uppercase() -> None:
    assert validate_password_uppercase("T123456789") == "T123456789"
    with pytest.raises(ValidationError):
        validate_password_uppercase("1234567890")


def test_validate_password_symbol() -> None:
    assert validate_password_symbol("@123456789") == "@123456789"
    with pytest.raises(ValidationError):
        validate_password_symbol("1234567890")


def test_validate_password_lowercase() -> None:
    assert validate_password_lowercase("t123456789") == "t123456789"
    with pytest.raises(ValidationError):
        validate_password_lowercase("1234567890")
