#!/usr/bin/env python3
"""Migration script for JSON to SQLite data migration."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

def find_project_root() -> Path:
    """Find project root by looking for pyproject.toml."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    # Fallback: assume we're in scripts/ directory
    return Path(__file__).parent.parent

# Add src to path
project_root = find_project_root()
sys.path.insert(0, str(project_root / "src"))

from src.config.platform import Platform, PlatformDetector
from src.config.settings import Settings, get_settings
from src.db.sqlite_manager import SQLiteManager, get_db
from src.core.repositories import (
    ActivityRepository,
    FarmRepository,
    GameDataRepository,
    InventoryRepository,
    LeaderboardRepository,
    UserRepository,
)


class DataMigrator:
    """Handles migration from JSON files to SQLite database."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize migrator."""
        self.settings = settings or get_settings()
        self.db = get_db()
        self.data_dir = self._get_data_dir()

        # Initialize repositories
        self.user_repo = UserRepository(self.db)
        self.inventory_repo = InventoryRepository(self.db)
        self.farm_repo = FarmRepository(self.db)
        self.game_repo = GameDataRepository(self.db)
        self.leaderboard_repo = LeaderboardRepository(self.db)
        self.activity_repo = ActivityRepository(self.db)

    def _get_data_dir(self) -> Path:
        """Get data directory based on platform."""
        platform = PlatformDetector.detect()

        if platform == Platform.TERMUX:
            prefix = Path("/data/data/com.termux/files/usr")
            return Path("/data/data/com.termux/files/home/.hkkm")

        # Use settings data_dir
        return self.settings.data_dir

    def _load_json(self, filename: str) -> dict[str, Any] | list[Any] | None:
        """Load JSON file from data directory."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {filename}: {e}")
            return None

    def migrate_users(self) -> int:
        """Migrate users from users.json."""
        data = self._load_json("users.json")
        if not data:
            print("No users.json found, skipping user migration")
            return 0

        count = 0
        users = data if isinstance(data, list) else [data]

        for user_data in users:
            try:
                # Skip if user already exists
                existing = self.user_repo.get_by_username(user_data.get("username", ""))
                if existing:
                    print(f"  User '{user_data.get('username')}' already exists, skipping")
                    continue

                # Create user
                from src.core.models import User

                user = User.from_dict(user_data)

                # Insert directly to preserve ID
                import bcrypt

                password_hash = user.password_hash
                if not password_hash and user_data.get("password"):
                    # Hash the raw password if migrating old format
                    password_hash = bcrypt.hashpw(
                        user_data["password"].encode(), bcrypt.gensalt()
                    )

                self.db.execute(
                    """INSERT INTO users
                    (id, username, nickname, password_hash, xp, level, balance,
                     created_at, last_login, is_guest, unlocked_features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user.id,
                        user.username,
                        user.nickname,
                        password_hash,
                        user.xp,
                        user.level,
                        user.balance,
                        user.created_at.isoformat() if user.created_at else None,
                        user.last_login.isoformat() if user.last_login else None,
                        int(user.is_guest),
                        json.dumps(user.unlocked_features),
                    ),
                )

                # Migrate inventory
                self._migrate_user_inventory(user.id, user_data.get("inventory", {}))

                # Add to leaderboard
                self.leaderboard_repo.update_entry(
                    user.id, user.username, user.xp, user.balance
                )

                count += 1
                print(f"  Migrated user: {user.username}")

            except Exception as e:
                print(f"  Error migrating user {user_data.get('username', 'unknown')}: {e}")

        return count

    def _migrate_user_inventory(self, user_id: str, inventory: dict) -> None:
        """Migrate inventory items for a user."""
        from src.core.models.inventory import InventoryItem, ItemType

        # Map old categories to new item types
        type_mapping = {
            "tools": ItemType.TOOLS,
            "rods": ItemType.RODS,
            "baits": ItemType.BAITS,
            "seeds": ItemType.SEEDS,
            "feeds": ItemType.FEEDS,
            "fish": ItemType.FISH,
            "crops": ItemType.CROPS,
            "products": ItemType.PRODUCTS,
        }

        for category, items in inventory.items():
            item_type = type_mapping.get(category, category)

            if isinstance(items, dict):
                # Handle {item_id: quantity} format
                for item_id, quantity in items.items():
                    try:
                        self.inventory_repo.add_item(
                            user_id=user_id,
                            item_type=item_type.value if isinstance(item_type, ItemType) else item_type,
                            item_id=int(item_id),
                            quantity=int(quantity),
                        )
                    except (ValueError, TypeError) as e:
                        print(f"    Warning: Invalid item {item_id} in {category}: {e}")
            elif isinstance(items, list):
                # Handle list format
                for item in items:
                    if isinstance(item, dict):
                        try:
                            self.inventory_repo.add_item(
                                user_id=user_id,
                                item_type=item_type.value if isinstance(item_type, ItemType) else item_type,
                                item_id=item.get("id", 0),
                                quantity=item.get("quantity", 1),
                                metadata=item.get("metadata", {}),
                            )
                        except (ValueError, TypeError) as e:
                            print(f"    Warning: Invalid item in {category}: {e}")

    def migrate_game_data(self) -> bool:
        """Migrate static game data (fish, crops, animals, etc.)."""
        game_data: dict[str, list[dict[str, Any]]] = {}

        # Load all game data files
        for filename in ["fish.json", "crops.json", "seeds.json", "animals.json", "animal_products.json", "items.json"]:
            data = self._load_json(filename)
            if data:
                key = filename.replace(".json", "")
                game_data[key] = data if isinstance(data, list) else [data]
                print(f"  Loaded {len(game_data[key])} entries from {filename}")

        if not game_data:
            print("No game data files found, skipping")
            return False

        self.db.seed_game_data(game_data)
        print(f"Seeded game data: {', '.join(game_data.keys())}")
        return True

    def migrate_all(self) -> dict[str, Any]:
        """Run complete migration."""
        results = {
            "users": 0,
            "game_data": False,
            "errors": [],
        }

        print("=" * 50)
        print("Hikikimo Life Data Migration")
        print("=" * 50)
        print(f"Data directory: {self.data_dir}")
        print(f"Database: {self.settings.database_path}")
        print()

        # Migrate game data first (needed for foreign keys)
        print("Migrating game data...")
        try:
            results["game_data"] = self.migrate_game_data()
        except Exception as e:
            results["errors"].append(f"Game data: {e}")
            print(f"  Error: {e}")

        print()

        # Migrate users
        print("Migrating users...")
        try:
            results["users"] = self.migrate_users()
        except Exception as e:
            results["errors"].append(f"Users: {e}")
            print(f"  Error: {e}")

        print()
        print("=" * 50)
        print("Migration Summary")
        print("=" * 50)
        print(f"Users migrated: {results['users']}")
        print(f"Game data seeded: {results['game_data']}")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
            for err in results["errors"]:
                print(f"  - {err}")

        return results


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate Hikikimo Life data to SQLite")
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Override data directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("Dry run mode - no changes will be made")

    # Initialize settings
    settings = get_settings()
    if args.data_dir:
        settings.data_dir = Path(args.data_dir)

    # Run migration
    migrator = DataMigrator(settings)
    results = migrator.migrate_all()

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
