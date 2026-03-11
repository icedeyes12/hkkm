"""User data model - Single player, no auth."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.core.models.inventory import InventoryItem


@dataclass
class User:
    """Player save data - single player game."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Player"
    xp: int = 0
    level: int = 1
    balance: int = 500
    inventory: list[InventoryItem] = field(default_factory=list)
    unlocked_features: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_played: datetime = field(default_factory=datetime.now)

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def xp_to_next_level(self) -> int:
        import math
        needed = int(100 * math.pow(self.level, 1.5))
        return max(0, needed - self.xp)

    @property
    def total_xp_for_level(self) -> int:
        import math
        return int(100 * math.pow(self.level, 1.5))

    def add_xp(self, amount: int) -> bool:
        self.xp += amount
        old_level = self.level
        while self.xp >= self.total_xp_for_level:
            self.xp -= self.total_xp_for_level
            self.level += 1
        return self.level > old_level

    def can_afford(self, amount: int) -> bool:
        return self.balance >= amount

    def deduct(self, amount: int) -> bool:
        if not self.can_afford(amount):
            return False
        self.balance -= amount
        return True

    def credit(self, amount: int) -> None:
        self.balance += amount

    @classmethod
    def create_single_player(cls) -> User:
        """Create new single player save."""
        return cls(
            name="Player",
            balance=500,
            level=1,
            xp=0,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "xp": self.xp,
            "level": self.level,
            "balance": self.balance,
            "inventory": [item.to_dict() for item in self.inventory],
            "unlocked_features": self.unlocked_features,
            "created_at": self.created_at.isoformat(),
            "last_played": self.last_played.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        user = cls(
            id=data.get("id", str(uuid4())),
            name=data.get("name", "Player"),
            xp=data.get("xp", 0),
            level=data.get("level", 1),
            balance=data.get("balance", 500),
            inventory=[InventoryItem.from_dict(item) for item in data.get("inventory", [])],
            unlocked_features=data.get("unlocked_features", {}),
        )
        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_played"):
            user.last_played = datetime.fromisoformat(data["last_played"])
        return user
