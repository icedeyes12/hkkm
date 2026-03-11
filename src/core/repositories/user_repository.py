"""User data repository."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import bcrypt

from src.core.exceptions import UsernameExistsError, UserNotFoundError, ValidationError
from src.core.models import User
from src.core.models.inventory import InventoryItem
from src.db.sqlite_manager import SQLiteManager


class UserRepository:
    """Repository for user data operations."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        row = self.db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        if not row:
            return None
        return self._row_to_user(row)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        row = self.db.fetchone(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not row:
            return None
        return self._row_to_user(row)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with password.

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = self.get_by_username(username)
        if not user or not user.password_hash:
            return None

        if bcrypt.checkpw(password.encode(), user.password_hash):
            # Update last login
            self.update_last_login(user.id)
            return user

        return None

    def create(
        self,
        username: str,
        password: str,
        nickname: Optional[str] = None,
        is_guest: bool = False,
    ) -> User:
        """Create a new user.

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            nickname: Display name (defaults to username)
            is_guest: Whether this is a guest account

        Returns:
            Created user

        Raises:
            UsernameExistsError: If username already taken
        """
        # Check if username exists
        if self.get_by_username(username):
            raise UsernameExistsError(f"Username '{username}' already exists")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        user = User(
            username=username,
            nickname=nickname or username,
            password_hash=password_hash,
            is_guest=is_guest,
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
                user.password_hash,
                user.xp,
                user.level,
                user.balance,
                user.created_at.isoformat(),
                None,
                int(user.is_guest),
                json.dumps(user.unlocked_features),
            ),
        )

        # Add to leaderboard
        self.db.execute(
            "INSERT INTO leaderboard (user_id, username, xp, balance) VALUES (?, ?, ?, ?)",
            (user.id, user.username, user.xp, user.balance),
        )

        return user

    def create_guest(self) -> User:
        """Create a temporary guest user."""
        import uuid

        guest_id = f"guest_{uuid.uuid4().hex[:8]}"
        return self.create(
            username=guest_id,
            password=uuid.uuid4().hex,  # Random password, won't be used
            nickname="Guest",
            is_guest=True,
        )

    def update(self, user: User) -> None:
        """Update user data."""
        self.db.execute(
            """UPDATE users SET
            nickname = ?, xp = ?, level = ?, balance = ?,
            unlocked_features = ?, is_guest = ?
            WHERE id = ?""",
            (
                user.nickname,
                user.xp,
                user.level,
                user.balance,
                json.dumps(user.unlocked_features),
                int(user.is_guest),
                user.id,
            ),
        )

        # Update leaderboard
        self.db.execute(
            """UPDATE leaderboard SET
            username = ?, xp = ?, balance = ?, last_updated = ?
            WHERE user_id = ?""",
            (user.username, user.xp, user.balance, datetime.now().isoformat(), user.id),
        )

    def update_last_login(self, user_id: str) -> None:
        """Update user's last login time."""
        self.db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id),
        )

    def delete(self, user_id: str) -> bool:
        """Delete user and all associated data.

        Returns:
            True if user was deleted, False if not found
        """
        result = self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return result.rowcount > 0

    def update_password(self, user_id: str, new_password: str) -> None:
        """Update user password."""
        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        self.db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )

    def add_xp(self, user_id: str, amount: int) -> tuple[int, bool]:
        """Add XP to user and check for level up.

        Returns:
            Tuple of (new XP, whether level up occurred)
        """
        user = self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        old_level = user.level
        leveled_up = user.add_xp(amount)

        self.update(user)
        return user.xp, leveled_up

    def _row_to_user(self, row: dict) -> User:
        """Convert database row to User model."""
        user = User(
            id=row["id"],
            username=row["username"],
            nickname=row["nickname"],
            password_hash=row["password_hash"],
            xp=row["xp"],
            level=row["level"],
            balance=row["balance"],
            is_guest=bool(row["is_guest"]),
            unlocked_features=json.loads(row["unlocked_features"] or "{}"),
        )

        if row["created_at"]:
            user.created_at = datetime.fromisoformat(row["created_at"])
        if row["last_login"]:
            user.last_login = datetime.fromisoformat(row["last_login"])

        # Load inventory
        user.inventory = self._load_inventory(user.id)

        return user

    def _load_inventory(self, user_id: str) -> list[InventoryItem]:
        """Load user's inventory."""
        rows = self.db.fetchall(
            "SELECT * FROM inventory WHERE user_id = ?",
            (user_id,)
        )

        return [
            InventoryItem(
                item_type=row["item_type"],
                item_id=row["item_id"],
                quantity=row["quantity"],
                metadata=json.loads(row["metadata"] or "{}"),
            )
            for row in rows
        ]

    def save_inventory(self, user_id: str, inventory: list[InventoryItem]) -> None:
        """Save user's inventory."""
        # Clear existing
        self.db.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))

        # Insert new
        if inventory:
            self.db.executemany(
                """INSERT INTO inventory
                (user_id, item_type, item_id, quantity, acquired_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        user_id,
                        item.item_type_str,
                        item.item_id,
                        item.quantity,
                        item.acquired_at.isoformat(),
                        json.dumps(item.metadata),
                    )
                    for item in inventory
                ],
            )
