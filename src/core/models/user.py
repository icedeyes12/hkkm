"""User data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from src.core.models.inventory import InventoryItem


@dataclass
class User:
    """User account data."""

    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    nickname: str = ""
    password_hash: Optional[bytes] = None
    xp: int = 0
    level: int = 1
    balance: int = 500
    inventory: list[InventoryItem] = field(default_factory=list)
    unlocked_features: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_guest: bool = False

    def __post_init__(self) -> None:
        """Set nickname to username if not provided."""
        if not self.nickname and self.username:
            self.nickname = self.username

    @property
    def display_name(self) -> str:
        """Get display name (nickname preferred)."""
        return self.nickname or self.username or "Guest"

    @property
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level."""
        # Exponential growth: base 100 * level^1.5
        import math
        needed = int(100 * math.pow(self.level, 1.5))
        return max(0, needed - self.xp)

    @property
    def total_xp_for_level(self) -> int:
        """Calculate total XP required for current level."""
        import math
        return int(100 * math.pow(self.level, 1.5))

    def add_xp(self, amount: int) -> bool:
        """Add XP and check for level up.

        Args:
            amount: XP amount to add

        Returns:
            True if level up occurred
        """
        self.xp += amount
        old_level = self.level

        # Check level ups
        while self.xp >= self.total_xp_for_level:
            self.xp -= self.total_xp_for_level
            self.level += 1

        return self.level > old_level

    def can_afford(self, amount: int) -> bool:
        """Check if user has sufficient balance."""
        return self.balance >= amount

    def deduct(self, amount: int) -> bool:
        """Deduct from balance if possible.

        Args:
            amount: Amount to deduct

        Returns:
            True if deduction was successful
        """
        if not self.can_afford(amount):
            return False
        self.balance -= amount
        return True

    def credit(self, amount: int) -> None:
        """Add to balance."""
        self.balance += amount

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "password_hash": self.password_hash.hex() if self.password_hash else None,
            "xp": self.xp,
            "level": self.level,
            "balance": self.balance,
            "inventory": [item.to_dict() for item in self.inventory],
            "unlocked_features": self.unlocked_features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_guest": self.is_guest,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create User from dictionary."""
        user = cls(
            id=data.get("id", str(uuid4())),
            username=data.get("username", ""),
            nickname=data.get("nickname", ""),
            password_hash=bytes.fromhex(data["password_hash"]) if data.get("password_hash") else None,
            xp=data.get("xp", 0),
            level=data.get("level", 1),
            balance=data.get("balance", 500),
            inventory=[InventoryItem.from_dict(item) for item in data.get("inventory", [])],
            unlocked_features=data.get("unlocked_features", {}),
            is_guest=data.get("is_guest", False),
        )

        # Parse dates
        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_login"):
            user.last_login = datetime.fromisoformat(data["last_login"])

        return user

    @classmethod
    def create(cls, username: str, nickname: str, password: str) -> User:
        """Create a new user with hashed password.

        Args:
            username: Unique username
            nickname: Display name
            password: Plain text password (will be hashed)

        Returns:
            New User instance ready to be saved
        """
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return cls(
            username=username,
            nickname=nickname,
            password_hash=password_hash,
            xp=0,
            level=1,
            balance=500,
            inventory=[],
            unlocked_features={},
            is_guest=False,
        )
