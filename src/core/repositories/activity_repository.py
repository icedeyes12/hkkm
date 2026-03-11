"""Activity log repository for audit/debugging."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional

from src.db.sqlite_manager import SQLiteManager


class ActivityRepository:
    """Repository for activity logging."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> int:
        """Log an activity.

        Args:
            action: Action name (e.g., 'login', 'purchase', 'harvest')
            user_id: Optional user ID
            details: Optional JSON-serializable details

        Returns:
            ID of the logged entry
        """
        cursor = self.db.execute(
            """INSERT INTO activity_log (user_id, action, details, created_at)
            VALUES (?, ?, ?, ?)""",
            (
                user_id,
                action,
                json.dumps(details) if details else None,
                datetime.now().isoformat(),
            ),
        )
        return cursor.lastrowid

    def get_recent(
        self,
        limit: int = 100,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
    ) -> list[dict]:
        """Get recent activity logs.

        Args:
            limit: Maximum entries to return
            user_id: Filter by user
            action: Filter by action type

        Returns:
            List of activity entries
        """
        where_clauses = []
        params: list = []

        if user_id:
            where_clauses.append("user_id = ?")
            params.append(user_id)
        if action:
            where_clauses.append("action = ?")
            params.append(action)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        rows = self.db.fetchall(
            f"""SELECT * FROM activity_log
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ?""",
            (*params, limit),
        )

        return [self._row_to_dict(row) for row in rows]

    def get_user_activity(
        self,
        user_id: str,
        since: Optional[datetime] = None,
        action: Optional[str] = None,
    ) -> list[dict]:
        """Get activity for a specific user.

        Args:
            user_id: User to query
            since: Only return entries after this time
            action: Filter by action type

        Returns:
            List of activity entries
        """
        where_clauses = ["user_id = ?"]
        params: list = [user_id]

        if since:
            where_clauses.append("created_at >= ?")
            params.append(since.isoformat())
        if action:
            where_clauses.append("action = ?")
            params.append(action)

        where_sql = " AND ".join(where_clauses)

        rows = self.db.fetchall(
            f"""SELECT * FROM activity_log
            WHERE {where_sql}
            ORDER BY created_at DESC""",
            tuple(params),
        )

        return [self._row_to_dict(row) for row in rows]

    def get_action_counts(
        self,
        since: Optional[datetime] = None,
        user_id: Optional[str] = None,
    ) -> dict[str, int]:
        """Get counts of each action type.

        Args:
            since: Only count entries after this time
            user_id: Filter by user

        Returns:
            Dictionary of action -> count
        """
        where_clauses: list[str] = []
        params: list = []

        if since:
            where_clauses.append("created_at >= ?")
            params.append(since.isoformat())
        if user_id:
            where_clauses.append("user_id = ?")
            params.append(user_id)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        rows = self.db.fetchall(
            f"""SELECT action, COUNT(*) as count
            FROM activity_log
            {where_sql}
            GROUP BY action""",
            tuple(params),
        )

        return {row["action"]: row["count"] for row in rows}

    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove entries older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of entries removed
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        result = self.db.execute(
            "DELETE FROM activity_log WHERE created_at < ?",
            (cutoff,),
        )
        return result.rowcount

    def get_stats(self, days: int = 7) -> dict:
        """Get activity statistics.

        Args:
            days: Time window in days

        Returns:
            Statistics dictionary
        """
        since = datetime.now() - timedelta(days=days)

        total_row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM activity_log WHERE created_at >= ?",
            (since.isoformat(),),
        )

        unique_users_row = self.db.fetchone(
            """SELECT COUNT(DISTINCT user_id) as count
            FROM activity_log WHERE created_at >= ?""",
            (since.isoformat(),),
        )

        action_counts = self.get_action_counts(since=since)

        return {
            "total_entries": total_row["count"] if total_row else 0,
            "unique_users": unique_users_row["count"] if unique_users_row else 0,
            "action_breakdown": action_counts,
            "period_days": days,
        }

    def _row_to_dict(self, row: dict) -> dict:
        """Convert row to dictionary."""
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "action": row["action"],
            "details": json.loads(row["details"]) if row["details"] else None,
            "created_at": row["created_at"],
        }
