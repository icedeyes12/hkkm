"""Integration tests for database layer."""

import pytest
import tempfile
from pathlib import Path

from src.db.sqlite_manager import SQLiteManager
from src.core.repositories.user_repository import UserRepository
from src.core.models.user import User


class TestDatabase:
    """Integration tests for database operations."""

    @pytest.fixture
    def db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        db = SQLiteManager(db_path)
        yield db
        # Cleanup
        import os
        os.unlink(db_path)

    @pytest.fixture
    def user_repo(self, db):
        """Create user repository."""
        return UserRepository()

    def test_user_crud(self, user_repo):
        """Test user create, read, update, delete."""
        # Create
        user = User.create("testuser", "Test User", "password123")
        user_repo.create(user)

        # Read
        found = user_repo.get_by_username("testuser")
        assert found is not None
        assert found.username == "testuser"
        assert found.nickname == "Test User"

        # Update
        found.nickname = "Updated Name"
        user_repo.update(found)

        updated = user_repo.get_by_id(user.id)
        assert updated.nickname == "Updated Name"

        # List
        users = user_repo.list_all()
        assert len(users) >= 1

    def test_password_verification(self, user_repo):
        """Test password verification works after storage."""
        user = User.create("pwdtest", "Pwd Test", "secretpass")
        user_repo.create(user)

        found = user_repo.get_by_username("pwdtest")
        assert found.verify_password("secretpass")
        assert not found.verify_password("wrongpass")

    def test_balance_update(self, user_repo):
        """Test balance updates."""
        user = User.create("baltest", "Balance Test", "pass")
        user_repo.create(user)

        # Add coins
        user.add_coins(500)
        user_repo.update(user)

        found = user_repo.get_by_username("baltest")
        assert found.balance == 1000  # 500 starting + 500 added

    def test_xp_and_level(self, user_repo):
        """Test XP and level progression stored correctly."""
        user = User.create("xptest", "XP Test", "pass")
        user_repo.create(user)

        # Add XP to level up
        leveled = user.add_xp(150)  # Should level to 2
        user_repo.update(user)

        found = user_repo.get_by_username("xptest")
        assert found.level == 2
        assert found.xp == 150


class TestInventoryRepository:
    """Tests for inventory repository."""

    @pytest.fixture
    def db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        db = SQLiteManager(db_path)
        yield db
        import os
        os.unlink(db_path)

    @pytest.fixture
    def inventory_repo(self, db):
        """Create inventory repository."""
        from src.core.repositories.inventory_repository import InventoryRepository
        return InventoryRepository()

    @pytest.fixture
    def user_repo(self, db):
        """Create user repository."""
        return UserRepository()

    def test_add_item(self, inventory_repo, user_repo):
        """Test adding item to inventory."""
        from src.core.repositories.inventory_repository import ItemType

        user = User.create("invtest", "Inventory Test", "pass")
        user_repo.create(user)

        inventory_repo.add_item(user.id, ItemType.FISH, 1, quantity=5)

        items = inventory_repo.get_user_inventory(user.id)
        assert len(items) == 1
        assert items[0].quantity == 5

    def test_remove_item(self, inventory_repo, user_repo):
        """Test removing items."""
        from src.core.repositories.inventory_repository import ItemType

        user = User.create("remtest", "Remove Test", "pass")
        user_repo.create(user)

        inventory_repo.add_item(user.id, ItemType.TOOL, 1, quantity=10)
        result = inventory_repo.remove_item(user.id, ItemType.TOOL, 1, 3)

        assert result is True
        items = inventory_repo.get_items_by_type(user.id, ItemType.TOOL)
        assert items[0].quantity == 7

    def test_get_by_type(self, inventory_repo, user_repo):
        """Test filtering inventory by type."""
        from src.core.repositories.inventory_repository import ItemType

        user = User.create("typetest", "Type Test", "pass")
        user_repo.create(user)

        inventory_repo.add_item(user.id, ItemType.FISH, 1, 5)
        inventory_repo.add_item(user.id, ItemType.ROD, 2, 1)
        inventory_repo.add_item(user.id, ItemType.FISH, 3, 3)

        fish_items = inventory_repo.get_items_by_type(user.id, ItemType.FISH)
        assert len(fish_items) == 2

        rod_items = inventory_repo.get_items_by_type(user.id, ItemType.ROD)
        assert len(rod_items) == 1
