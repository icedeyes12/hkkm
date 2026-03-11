"""User repository - Single player, no auth."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from src.core.models import User
from src.db.sqlite_manager import SQLiteManager


class UserRepository:
    """Repository for single player save data."""

    SINGLE_PLAYER_ID = "single_player"

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        self.db = db or SQLiteManager()

    def get_single_player(self) -> Optional[User]:
        """Load single player save."""
        row = self.db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (self.SINGLE_PLAYER_ID,)
        )
        if not row:
            return None
        return self._row_to_user(row)

    def save_single_player(self, user: User) -> None:
        """Save single player data."""
        # Force single player ID
        user.id = self.SINGLE_PLAYER_ID
        
        self.db.execute(
            """INSERT OR REPLACE INTO users
            (id, name, xp, level, balance, inventory, unlocked_features,
             created_at, last_played)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user.id,
                user.name,
                user.xp,
                user.level,
                user.balance,
                json.dumps([item.to_dict() for item in user.inventory]),
                json.dumps(user.unlocked_features),
                user.created_at.isoformat(),
                datetime.now().isoformat(),
            ),
        )

    def delete_single_player(self) -> None:
        """Delete single player save (reset)."""
        self.db.execute("DELETE FROM users WHERE id = ?", (self.SINGLE_PLAYER_ID,))
        # Also clear inventory
        self.db.execute("DELETE FROM inventory WHERE user_id = ?", (self.SINGLE_PLAYER_ID,))
        self.db.execute("DELETE FROM field_plots WHERE user_id = ?", (self.SINGLE_PLAYER_ID,))
        self.db.execute("DELETE FROM barn_slots WHERE user_id = ?", (self.SINGLE_PLAYER_ID,))

    def update_stats(self, user: User) -> None:
        """Update player stats (XP, level, balance)."""
        self.db.execute(
            """UPDATE users SET
            name = ?, xp = ?, level = ?, balance = ?,
            unlocked_features = ?, last_played = ?
            WHERE id = ?""",
            (
                user.name,
                user.xp,
                user.level,
                user.balance,
                json.dumps(user.unlocked_features),
                datetime.now().isoformat(),
                self.SINGLE_PLAYER_ID,
            ),
        )

    def _row_to_user(self, row: dict) -> User:
        """Convert database row to User."""
        user = User(
            id=row["id"],
            name=row["name"],
            xp=row["xp"],
            level=row["level"],
            balance=row["balance"],
            unlocked_features=json.loads(row["unlocked_features"] or "{}"),
        )
        
        # Parse dates
        if row.get("created_at"):
            user.created_at = datetime.fromisoformat(row["created_at"])
        if row.get("last_played"):
            user.last_played = datetime.fromisoformat(row["last_played"])
        
        # Load inventory
        if row.get("inventory"):
            from src.core.models.inventory import InventoryItem
            user.inventory = [InventoryItem.from_dict(item) for item in json.loads(row["inventory"])]
        
        return user
