"""Job Center widget with Work, Trade, and Crime options."""

from __future__ import annotations

import random
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, ProgressBar, Static

from src.core.models.user import User
from src.core.repositories.activity_repository import ActivityRepository
from src.core.repositories.user_repository import UserRepository
from src.core.services.economy_service import EconomyService


class JobCenterWidget(Static):
    """Job Center section with Work, Trade, and Crime options."""

    working = reactive(False)
    work_progress = reactive(0)

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.user_repo = UserRepository()
        self.activity_repo = ActivityRepository()
        self.economy = EconomyService()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("💼 Job Center", classes="section-title")
            yield Static("Choose your path to earn coins and XP")

            with Grid(id="job-grid"):
                # Work card
                with Vertical(classes="job-card"):
                    yield Label("🔨 Work", classes="title")
                    yield Static("Honest labor for steady income", classes="description")
                    yield Static(f"Rate: ~{self.economy.get_work_reward(self.user.level)} coins/work")
                    with Horizontal():
                        yield Button("Work Once", id="btn-work-once")
                        yield Button("Work ×10", id="btn-work-10")
                    yield Static("", id="work-result")

                # Trade card
                with Vertical(classes="job-card"):
                    yield Label("📊 Trade", classes="title")
                    yield Static("Buy low, sell high", classes="description")
                    yield Static("Market rates fluctuate hourly")
                    yield Button("Open Trading Post", id="btn-trade")
                    yield Static("", id="trade-status")

                # Crime card
                with Vertical(classes="job-card"):
                    yield Label("🗡️ Crime", classes="title")
                    yield Static("High risk, high reward", classes="description")
                    yield Static("⚠️ Risk: Lose coins or get caught!", classes="warning")
                    with Horizontal():
                        yield Button("Pickpocket", id="btn-crime-1")
                        yield Button("Heist", id="btn-crime-2")
                    yield Static("", id="crime-result")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-work-once":
            self._do_work(1)
        elif btn_id == "btn-work-10":
            self._do_work(10)
        elif btn_id == "btn-trade":
            self._open_trading()
        elif btn_id.startswith("btn-crime-"):
            crime_type = 1 if btn_id == "btn-crime-1" else 2
            self._do_crime(crime_type)

    def _do_work(self, times: int):
        """Perform work action."""
        result_static = self.query_one("#work-result", Static)
        total_coins = 0
        total_xp = 0

        for _ in range(times):
            coins, xp = self.economy.work(self.user)
            total_coins += coins
            total_xp += xp
            self.user.add_coins(coins)
            self.user.add_xp(xp)

        self.user_repo.update(self.user)
        self.activity_repo.log(self.user.id, "work", {"times": times, "coins": total_coins, "xp": total_xp})

        result_static.update(f"✅ Worked {times}x: +{total_coins}🪙 +{total_xp}⭐")
        self._refresh_parent_stats()

    def _open_trading(self):
        """Open trading interface."""
        self.app.push_screen(TradingScreen(self.user))

    def _do_crime(self, crime_type: int):
        """Attempt crime action."""
        result_static = self.query_one("#crime-result", Static)

        success, message, coins, xp = self.economy.crime(self.user, crime_type)

        if success:
            self.user.add_coins(coins)
            self.user.add_xp(xp)
            self.user_repo.update(self.user)
            result_static.update(f"✅ {message}: +{coins}🪙 +{xp}⭐")
        else:
            if coins < 0:
                self.user.deduct(-coins)
                self.user_repo.update(self.user)
            result_static.update(f"❌ {message}")

        self.activity_repo.log(self.user.id, "crime", {"type": crime_type, "success": success, "coins": coins})
        self._refresh_parent_stats()

    def _refresh_parent_stats(self):
        """Refresh stats in parent screen."""
        try:
            parent = self.parent
            if isinstance(parent, Vertical):
                screen = parent.parent
                if hasattr(screen, "refresh_user_stats"):
                    screen.refresh_user_stats()
        except:
            pass


from src.tui.screens.trading_screen import TradingScreen
from textual.widgets import Button
