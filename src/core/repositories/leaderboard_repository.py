"""Leaderboard repository for rankings."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.db.sqlite_manager import SQLiteManager


class LeaderboardRepository:
    """Repository for leaderboard operations."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    def get_xp_ranking(self, limit: int = 100) -> list[dict]:
        """Get XP leaderboard ranking.

        Returns:
            List of {rank, user_id, username, xp, level}
        """
        rows = self.db.fetchall(
            """SELECT user_id, username, xp, balance,
                RANK() OVER (ORDER BY xp DESC) as rank
            FROM leaderboard
            ORDER BY xp DESC, last_updated ASC
            LIMIT ?""",
            (limit,),
        )
        return [
            {
                "rank": row["rank"],
                "user_id": row["user_id"],
                "username": row["username"],
                "xp": row["xp"],
                "balance": row["balance"],
            }
            for row in rows
        ]

    def get_wealth_ranking(self, limit: int = 100) -> list[dict]:
        """Get wealth (balance) leaderboard ranking.

        Returns:
            List of {rank, user_id, username, balance, xp}
        """
        rows = self.db.fetchall(
            """SELECT user_id, username, balance, xp,
                RANK() OVER (ORDER BY balance DESC) as rank
            FROM leaderboard
            ORDER BY balance DESC, last_updated ASC
            LIMIT ?""",
            (limit,),
        )
        return [
            {
                "rank": row["rank"],
                "user_id": row["user_id"],
                "username": row["username"],
                "balance": row["balance"],
                "xp": row["xp"],
            }
            for row in rows
        ]

    def get_user_xp_rank(self, user_id: str) -> Optional[int]:
        """Get a user's XP rank.

        Returns:
            Rank position or None if not found
        """
        row = self.db.fetchone(
            """SELECT rank FROM (
                SELECT user_id, RANK() OVER (ORDER BY xp DESC) as rank
                FROM leaderboard
            ) WHERE user_id = ?""",
            (user_id,),
        )
        return row["rank"] if row else None

    def get_user_wealth_rank(self, user_id: str) -> Optional[int]:
        """Get a user's wealth rank.

        Returns:
            Rank position or None if not found
        """
        row = self.db.fetchone(
            """SELECT rank FROM (
                SELECT user_id, RANK() OVER (ORDER BY balance DESC) as rank
                FROM leaderboard
            ) WHERE user_id = ?""",
            (user_id,),
        )
        return row["rank"] if row else None

    def update_entry(
        self,
        user_id: str,
        username: str,
        xp: int,
        balance: int,
    ) -> None:
        """Update or create leaderboard entry."""
        self.db.execute(
            """INSERT INTO leaderboard (user_id, username, xp, balance, last_updated)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            xp = excluded.xp,
            balance = excluded.balance,
            last_updated = excluded.last_updated""",
            (user_id, username, xp, balance, datetime.now().isoformat()),
        )

    def get_surrounding_users(
        self,
        user_id: str,
        radius: int = 5,
        by_xp: bool = True,
    ) -> list[dict]:
        """Get users ranked near a specific user.

        Args:
            user_id: Target user
            radius: Number of users above and below
            by_xp: True for XP ranking, False for wealth

        Returns:
            List of surrounding users with rank info
        """
        order_col = "xp" if by_xp else "balance"

        # Get user's rank first
        rank_row = self.db.fetchone(
            f"""SELECT rank FROM (
                SELECT user_id, RANK() OVER (ORDER BY {order_col} DESC) as rank
                FROM leaderboard
            ) WHERE user_id = ?""",
            (user_id,),
        )

        if not rank_row:
            return []

        user_rank = rank_row["rank"]
        start_rank = max(1, user_rank - radius)
        end_rank = user_rank + radius

        rows = self.db.fetchall(
            f"""SELECT user_id, username, xp, balance,
                RANK() OVER (ORDER BY {order_col} DESC) as rank
            FROM leaderboard
            QUALIFY rank BETWEEN ? AND ?
            ORDER BY {order_col} DESC""",
            (start_rank, end_rank),
        )

        return [
            {
                "rank": row["rank"],
                "user_id": row["user_id"],
                "username": row["username"],
                "xp": row["xp"],
                "balance": row["balance"],
                "is_target": row["user_id"] == user_id,
            }
            for row in rows
        ]

    def get_top_users(self, category: str = "xp", limit: int = 10) -> list[dict]:
        """Get top users by category.

        Args:
            category: 'xp' or 'wealth'
            limit: Number of top users

        Returns:
            List of top users
        """
        if category == "xp":
            return self.get_xp_ranking(limit)
        return self.get_wealth_ranking(limit)

    def remove_user(self, user_id: str) -> bool:
        """Remove user from leaderboard."""
        result = self.db.execute(
            "DELETE FROM leaderboard WHERE user_id = ?",
            (user_id,),
        )
        return result.rowcount > 0

    def get_stats(self) -> dict:
        """Get leaderboard statistics."""
        row = self.db.fetchone(
            """SELECT
                COUNT(*) as total_users,
                MAX(xp) as max_xp,
                MAX(balance) as max_balance,
                AVG(xp) as avg_xp,
                AVG(balance) as avg_balance
            FROM leaderboard"""
        )

        if not row:
            return {
                "total_users": 0,
                "max_xp": 0,
                "max_balance": 0,
                "avg_xp": 0,
                "avg_balance": 0,
            }

        return {
            "total_users": row["total_users"],
            "max_xp": row["max_xp"] or 0,
            "max_balance": row["max_balance"] or 0,
            "avg_xp": round(row["avg_xp"] or 0, 2),
            "avg_balance": round(row["avg_balance"] or 0, 2),
        }
