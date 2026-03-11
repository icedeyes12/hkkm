"""Leaderboard widget showing rankings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Label, Static

from src.core.models.user import User
from src.core.repositories.leaderboard_repository import UserRepository


class LeaderboardWidget(Static):
    """Leaderboard section with rankings."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.leaderboard_repo = UserRepository()
        self.current_tab = "xp"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🏆 Leaderboard", classes="section-title")

            with Vertical():
                yield Button("By XP", id="tab-xp", variant="primary")
                yield Button("By Wealth", id="tab-wealth")

            table = DataTable(id="leaderboard-table")
            table.cursor_type = "row"
            yield table

            yield Static("", id="leaderboard-info")

    def on_mount(self):
        """Load initial data."""
        self._load_xp_leaderboard()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab buttons."""
        btn_id = event.button.id
        if btn_id == "tab-xp":
            self.current_tab = "xp"
            self._update_buttons()
            self._load_xp_leaderboard()
        elif btn_id == "tab-wealth":
            self.current_tab = "wealth"
            self._update_buttons()
            self._load_wealth_leaderboard()

    def _update_buttons(self):
        """Update button styling."""
        xp_btn = self.query_one("#tab-xp", Button)
        wealth_btn = self.query_one("#tab-wealth", Button)
        xp_btn.variant = "primary" if self.current_tab == "xp" else "default"
        wealth_btn.variant = "primary" if self.current_tab == "wealth" else "default"

    def _load_xp_leaderboard(self):
        """Load XP rankings."""
        table = self.query_one("#leaderboard-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Rank", "Player", "Level", "XP")

        entries = self.leaderboard_repo.get_xp_leaderboard(limit=20)
        user_rank = None

        for entry in entries:
            is_user = entry["user_id"] == self.user.id
            rank_marker = "👉" if is_user else ""
            table.add_row(
                f"{rank_marker} #{entry['rank']}",
                entry["username"],
                str(entry["level"]),
                str(entry["xp"]),
            )
            if is_user:
                user_rank = entry["rank"]

        info = self.query_one("#leaderboard-info", Static)
        if user_rank:
            info.update(f"Your rank: #{user_rank} | XP: {self.user.xp}")
        else:
            info.update(f"Your XP: {self.user.xp} (not ranked yet)")

    def _load_wealth_leaderboard(self):
        """Load wealth rankings."""
        table = self.query_one("#leaderboard-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Rank", "Player", "Balance")

        entries = self.leaderboard_repo.get_wealth_leaderboard(limit=20)
        user_rank = None

        for entry in entries:
            is_user = entry["user_id"] == self.user.id
            rank_marker = "👉" if is_user else ""
            table.add_row(
                f"{rank_marker} #{entry['rank']}",
                entry["username"],
                f"{entry['balance']} 🪙",
            )
            if is_user:
                user_rank = entry["rank"]

        info = self.query_one("#leaderboard-info", Static)
        if user_rank:
            info.update(f"Your rank: #{user_rank} | Balance: {self.user.balance} 🪙")
        else:
            info.update(f"Your balance: {self.user.balance} 🪙 (not ranked yet)")
