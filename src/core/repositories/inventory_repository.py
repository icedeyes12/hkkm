"""Inventory repository for item management."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from src.core.exceptions import ItemNotFoundError, ValidationError
from src.core.models.inventory import InventoryItem, ItemType
from src.db.sqlite_manager import SQLiteManager


class InventoryRepository:
    """Repository for inventory operations."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    def get_items(
        self,
        user_id: str,
        item_type: Optional[str | ItemType] = None,
    ) -> list[InventoryItem]:
        """Get user's inventory items.

        Args:
            user_id: User ID
            item_type: Optional filter by item type

        Returns:
            List of inventory items
        """
        if item_type:
            type_str = item_type.value if isinstance(item_type, ItemType) else item_type
            rows = self.db.fetchall(
                "SELECT * FROM inventory WHERE user_id = ? AND item_type = ?",
                (user_id, type_str),
            )
        else:
            rows = self.db.fetchall(
                "SELECT * FROM inventory WHERE user_id = ?",
                (user_id,),
            )

        return [self._row_to_item(row) for row in rows]

    def get_item(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
    ) -> Optional[InventoryItem]:
        """Get specific item from inventory."""
        type_str = item_type.value if isinstance(item_type, ItemType) else item_type

        row = self.db.fetchone(
            "SELECT * FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?",
            (user_id, type_str, item_id),
        )

        if not row:
            return None
        return self._row_to_item(row)

    def get_quantity(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
    ) -> int:
        """Get quantity of specific item."""
        type_str = item_type.value if isinstance(item_type, ItemType) else item_type

        row = self.db.fetchone(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?",
            (user_id, type_str, item_id),
        )

        return row["quantity"] if row else 0

    def add_item(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
        quantity: int = 1,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add item to inventory.

        Args:
            user_id: User ID
            item_type: Type of item
            item_id: Item ID
            quantity: Amount to add (must be positive)
            metadata: Optional item metadata

        Raises:
            ValidationError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        type_str = item_type.value if isinstance(item_type, ItemType) else item_type

        # Check if item exists
        existing = self.get_item(user_id, item_type, item_id)

        if existing:
            # Update quantity
            new_quantity = existing.quantity + quantity
            self.db.execute(
                "UPDATE inventory SET quantity = ?, metadata = ? WHERE user_id = ? AND item_type = ? AND item_id = ?",
                (new_quantity, json.dumps(metadata or existing.metadata), user_id, type_str, item_id),
            )
        else:
            # Insert new
            self.db.execute(
                """INSERT INTO inventory
                (user_id, item_type, item_id, quantity, acquired_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, type_str, item_id, quantity, datetime.now().isoformat(), json.dumps(metadata or {})),
            )

    def remove_item(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
        quantity: int = 1,
    ) -> bool:
        """Remove item from inventory.

        Args:
            user_id: User ID
            item_type: Type of item
            item_id: Item ID
            quantity: Amount to remove

        Returns:
            True if removal successful, False if insufficient quantity

        Raises:
            ItemNotFoundError: If item not found in inventory
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        type_str = item_type.value if isinstance(item_type, ItemType) else item_type

        existing = self.get_item(user_id, item_type, item_id)
        if not existing:
            raise ItemNotFoundError(f"Item {item_type}/{item_id} not found in inventory")

        if existing.quantity < quantity:
            return False

        new_quantity = existing.quantity - quantity

        if new_quantity == 0:
            # Remove entirely
            self.db.execute(
                "DELETE FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?",
                (user_id, type_str, item_id),
            )
        else:
            # Update quantity
            self.db.execute(
                "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_type = ? AND item_id = ?",
                (new_quantity, user_id, type_str, item_id),
            )

        return True

    def update_metadata(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
        metadata: dict,
    ) -> None:
        """Update item metadata."""
        type_str = item_type.value if isinstance(item_type, ItemType) else item_type

        result = self.db.execute(
            "UPDATE inventory SET metadata = ? WHERE user_id = ? AND item_type = ? AND item_id = ?",
            (json.dumps(metadata), user_id, type_str, item_id),
        )

        if result.rowcount == 0:
            raise ItemNotFoundError(f"Item {item_type}/{item_id} not found")

    def clear_inventory(self, user_id: str) -> None:
        """Clear all items for a user."""
        self.db.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))

    def count_items(self, user_id: str, item_type: Optional[str | ItemType] = None) -> int:
        """Count total items in inventory."""
        if item_type:
            type_str = item_type.value if isinstance(item_type, ItemType) else item_type
            row = self.db.fetchone(
                "SELECT SUM(quantity) as total FROM inventory WHERE user_id = ? AND item_type = ?",
                (user_id, type_str),
            )
        else:
            row = self.db.fetchone(
                "SELECT SUM(quantity) as total FROM inventory WHERE user_id = ?",
                (user_id,),
            )

        return row["total"] or 0

    def has_item(
        self,
        user_id: str,
        item_type: str | ItemType,
        item_id: int,
        minimum_quantity: int = 1,
    ) -> bool:
        """Check if user has at least minimum_quantity of item."""
        return self.get_quantity(user_id, item_type, item_id) >= minimum_quantity

    def _row_to_item(self, row: dict) -> InventoryItem:
        """Convert database row to InventoryItem."""
        item = InventoryItem(
            item_type=row["item_type"],
            item_id=row["item_id"],
            quantity=row["quantity"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
        if row["acquired_at"]:
            item.acquired_at = datetime.fromisoformat(row["acquired_at"])
        return item
