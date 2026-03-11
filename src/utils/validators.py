"""Input validation utilities."""

from __future__ import annotations

import re
from typing import Optional

from src.core.exceptions import ValidationError


# Validation constants
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 32
NICKNAME_MIN_LENGTH = 1
NICKNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 6

# Username: alphanumeric + underscore, must start with letter
USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

# Nickname: printable characters, no control chars
NICKNAME_PATTERN = re.compile(r"^[\w\s\-\.!@#$%^&*()\[\]{}'\"]*$")


def validate_username(username: str) -> None:
    """Validate username format.

    Args:
        username: Username to validate

    Raises:
        ValidationError: If username is invalid
    """
    if not username:
        raise ValidationError("Username is required")

    if len(username) < USERNAME_MIN_LENGTH:
        raise ValidationError(
            f"Username must be at least {USERNAME_MIN_LENGTH} characters"
        )

    if len(username) > USERNAME_MAX_LENGTH:
        raise ValidationError(
            f"Username must be at most {USERNAME_MAX_LENGTH} characters"
        )

    if not USERNAME_PATTERN.match(username):
        raise ValidationError(
            "Username must start with a letter and contain only letters, numbers, and underscores"
        )


def validate_nickname(nickname: str) -> None:
    """Validate nickname format.

    Args:
        nickname: Nickname to validate

    Raises:
        ValidationError: If nickname is invalid
    """
    if not nickname:
        raise ValidationError("Nickname is required")

    if len(nickname) < NICKNAME_MIN_LENGTH:
        raise ValidationError(
            f"Nickname must be at least {NICKNAME_MIN_LENGTH} character"
        )

    if len(nickname) > NICKNAME_MAX_LENGTH:
        raise ValidationError(
            f"Nickname must be at most {NICKNAME_MAX_LENGTH} characters"
        )

    if not NICKNAME_PATTERN.match(nickname):
        raise ValidationError("Nickname contains invalid characters")


def validate_password(password: str) -> None:
    """Validate password strength.

    Args:
        password: Password to validate

    Raises:
        ValidationError: If password is too weak
    """
    if not password:
        raise ValidationError("Password is required")

    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
        )


def validate_positive_int(value: int, name: str = "Value") -> None:
    """Validate positive integer.

    Args:
        value: Value to validate
        name: Name of the value for error messages

    Raises:
        ValidationError: If not a positive integer
    """
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{name} must be a positive integer")


def validate_non_negative_int(value: int, name: str = "Value") -> None:
    """Validate non-negative integer.

    Args:
        value: Value to validate
        name: Name of the value for error messages

    Raises:
        ValidationError: If negative
    """
    if not isinstance(value, int) or value < 0:
        raise ValidationError(f"{name} must be a non-negative integer")


def validate_amount(value: int, name: str = "Amount") -> None:
    """Validate positive amount (currency).

    Args:
        value: Amount to validate
        name: Name for error messages

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer")

    if value <= 0:
        raise ValidationError(f"{name} must be positive")


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Strip control characters except newlines and tabs
    sanitized = "".join(
        char for char in text
        if char == "\n" or char == "\t" or (ord(char) >= 32 and ord(char) < 127)
    )

    # Truncate if too long
    return sanitized[:max_length]


def is_valid_email(email: str) -> bool:
    """Basic email validation.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(pattern.match(email))
