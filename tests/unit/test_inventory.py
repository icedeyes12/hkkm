"""Unit tests for inventory model."""

import pytest
from src.core.models.inventory import InventoryItem, ItemType


class TestInventoryItem:
    """Tests for inventory item model."""

    def test_create_item(self):
        """Test item creation."""
        item = InventoryItem(
            user_id="user123",
            item_type=ItemType.FISH,
            item_id=1,
            quantity=5,
        )
        assert item.user_id == "user123"
        assert item.item_type == ItemType.FISH
        assert item.quantity == 5

    def test_item_type_str(self):
        """Test item type string conversion."""
        item = InventoryItem(
            user_id="user123",
            item_type=ItemType.TOOL,
            item_id=1,
        )
        assert item.item_type_str == "tool"

    def test_from_string_type(self):
        """Test creating from string type."""
        item = InventoryItem.from_string_type("user123", "fish", 1, 3)
        assert item.item_type == ItemType.FISH
        assert item.quantity == 3

    def test_to_dict(self):
        """Test serialization."""
        item = InventoryItem(
            user_id="user123",
            item_type=ItemType.CROP,
            item_id=5,
            quantity=10,
        )
        data = item.to_dict()
        assert data["item_type"] == "crop"
        assert data["item_id"] == 5
        assert data["quantity"] == 10

    def test_from_dict(self):
        """Test deserialization."""
        data = {
            "user_id": "user123",
            "item_type": "tool",
            "item_id": 1,
            "quantity": 2,
        }
        item = InventoryItem.from_dict(data)
        assert item.item_type == ItemType.TOOL
        assert item.quantity == 2
