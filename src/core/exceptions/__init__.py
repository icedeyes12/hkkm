"""Custom exceptions for Hikikimo Life."""

from __future__ import annotations


class HikikimoError(Exception):
    """Base exception for all Hikikimo Life errors."""

    pass


class DatabaseError(HikikimoError):
    """Database operation errors."""

    pass


class ValidationError(HikikimoError):
    """Data validation errors."""

    pass


class AuthenticationError(HikikimoError):
    """User authentication errors."""

    pass


class AuthorizationError(HikikimoError):
    """Permission/authorization errors."""

    pass


class GameLogicError(HikikimoError):
    """Game logic/rule violations."""

    pass


class InsufficientFundsError(GameLogicError):
    """Not enough currency for transaction."""

    pass


class InsufficientXPError(GameLogicError):
    """Not enough XP for action."""

    pass


class InventoryFullError(GameLogicError):
    """Inventory capacity exceeded."""

    pass


class ItemNotFoundError(GameLogicError):
    """Requested item not found in inventory."""

    pass


class UserNotFoundError(AuthenticationError):
    """User account not found."""

    pass


class UsernameExistsError(ValidationError):
    """Username already taken."""

    pass


class MigrationError(DatabaseError):
    """Database migration failure."""

    pass
