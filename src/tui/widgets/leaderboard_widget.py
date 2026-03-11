"""Leaderboard widget - disabled for single player."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static

from src.core.models.user import User


class LeaderboardWidget(Static):
    """Leaderboard - single player mode (no online rankings)."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🏆 Leaderboard", classes="section-title")
            yield Static("Leaderboard is disabled in single player mode.")
            yield Static(f"Your Stats: Level {self.user.level} | XP: {self.user.xp} | Balance: {self.user.balance}🪙")
