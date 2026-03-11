"""Inventory item data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ItemType(Enum):
    """Types of inventory items."""

    TOOLS = "tools"
    RODS = "rods"
    BAITS = "baits"
    SEEDS = "seeds"
    FEEDS = "feeds"
    FISH = "fish"
    CROPS = "crops"
    PRODUCTS = "products"


@dataclass
class InventoryItem:
    """Single inventory item entry."""

    item_type: ItemType | str
    item_id: int
    quantity: int = 1
    acquired_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize item_type to enum if string."""
        if isinstance(self.item_type, str):
            try:
                self.item_type = ItemType(self.item_type.lower())
            except ValueError:
                pass  # Keep as custom string

    @property
    def item_type_str(self) -> str:
        """Get item type as string."""
        return self.item_type.value if isinstance(self.item_type, ItemType) else str(self.item_type)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item_type": self.item_type_str,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "acquired_at": self.acquired_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InventoryItem:
        """Create from dictionary."""
        item = cls(
            item_type=data.get("item_type", "unknown"),
            item_id=data.get("item_id", 0),
            quantity=data.get("quantity", 1),
            metadata=data.get("metadata", {}),
        )
        if data.get("acquired_at"):
            item.acquired_at = datetime.fromisoformat(data["acquired_at"])
        return item
