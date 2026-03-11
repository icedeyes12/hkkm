"""Daily rewards widget."""

from __future__ import annotations

from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Label, Static

from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository


class DailyWidget(Static):
    """Daily rewards section."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.user_repo = UserRepository()
        self.last_claimed = None  # Would be stored in user data

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📅 Daily Rewards", classes="section-title")

            # Calculate daily streak and reward
            streak = self._get_streak()
            reward = self._calculate_reward(streak)

            yield Static(f"🔥 Current Streak: {streak} days")
            yield Static(f"🎁 Today's Reward: {reward} 🪙")

            if self._can_claim():
                yield Button("🎁 Claim Daily Reward", id="btn-claim", variant="success")
            else:
                time_until = self._time_until_next()
                yield Static(f"⏰ Next reward in: {time_until}")
                yield Button("🎁 Already Claimed", id="btn-claimed", disabled=True)

            yield Static("", id="claim-result")

            yield Label("📋 Reward Schedule")
            for day in range(1, 8):
                r = self._calculate_reward(day)
                marker = "✅" if day <= streak else "⬜"
                yield Static(f"{marker} Day {day}: {r} 🪙")

    def _get_streak(self) -> int:
        """Get current streak (would be stored in database)."""
        # Placeholder - would track from user data
        return min(7, (self.user.xp // 100) % 7 + 1)

    def _calculate_reward(self, streak: int) -> int:
        """Calculate reward based on streak."""
        base = 100
        multiplier = min(streak, 7)
        return base * multiplier

    def _can_claim(self) -> bool:
        """Check if user can claim daily reward."""
        # Would check last_claimed timestamp
        return True  # Placeholder

    def _time_until_next(self) -> str:
        """Get time until next claim."""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        diff = tomorrow - now
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle claim button."""
        if event.button.id == "btn-claim":
            streak = self._get_streak()
            reward = self._calculate_reward(streak)

            self.user.add_coins(reward)
            self.user.add_xp(streak * 10)
            self.user_repo.update(self.user)

            result = self.query_one("#claim-result", Static)
            result.update(f"🎉 Claimed {reward} 🪙 and {streak * 10} ⭐ XP!")

            # Disable button
            event.button.disabled = True
            event.button.label = "Already Claimed"

            self._refresh_stats()

    def _refresh_stats(self):
        """Refresh parent stats."""
        try:
            parent = self.parent
            if parent and hasattr(parent, "refresh_user_stats"):
                parent.refresh_user_stats()
        except:
            pass
