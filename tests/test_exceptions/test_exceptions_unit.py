import pytest
from fastapi import status
from src.exceptions import (
    FrostiesException,
    InvalidAccessToken,
    InvalidRefreshToken,
    InvalidToken,
    AccountExists,
    NoAccountExists,
    IncorrectPassword,
    ExpiredToken,
    UserNotFound,
    FrostyNotFound,
    FrostyExists,
)

def test_frosties_exception_defaults():
    exc = FrostiesException(detail="test", status_code=418, foo="bar")
    assert exc.detail == "test"
    assert exc.status_code == 418
    assert getattr(exc, "foo") == "bar"

@pytest.mark.parametrize("exc_cls, expected_detail, expected_status", [
    (InvalidAccessToken, "Invalid access token provided.", status.HTTP_403_FORBIDDEN),
    (InvalidRefreshToken, "Invalid refresh token provided.", status.HTTP_403_FORBIDDEN),
    (InvalidToken, "Invalid or expired token provided.", status.HTTP_403_FORBIDDEN),
    (AccountExists, "Account already exists with this email.", status.HTTP_409_CONFLICT),
    (NoAccountExists, "No account exists for this email. Please signup.", status.HTTP_404_NOT_FOUND),
    (IncorrectPassword, "Password is incorrect.", status.HTTP_401_UNAUTHORIZED),
    (ExpiredToken, "Token has expired. Please login again.", status.HTTP_401_UNAUTHORIZED),
    (UserNotFound, "User not found.", status.HTTP_404_NOT_FOUND),
    (FrostyExists, "Frosty already exists.", status.HTTP_409_CONFLICT),
])
def test_exception_class_defaults(exc_cls, expected_detail, expected_status):
    exc = exc_cls()
    assert exc.detail == expected_detail
    assert exc.status_code == expected_status

def test_frosty_not_found_default_and_custom():
    exc = FrostyNotFound(frost_id=42)
    assert exc.detail == "Frost item with id 42 not found or unauthorized user."
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert getattr(exc, "frost_id") == 42

    exc2 = FrostyNotFound(frost_id=99, detail="Custom message")
    assert exc2.detail == "Custom message"
    assert getattr(exc2, "frost_id") == 99

def test_inheritance():
    assert issubclass(InvalidAccessToken, FrostiesException)
    assert issubclass(FrostyNotFound, FrostiesException)