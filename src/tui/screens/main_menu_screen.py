"""Main menu screen with sidebar navigation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.tui.widgets.job_center_widget import JobCenterWidget
from src.tui.widgets.casino_widget import CasinoWidget
from src.tui.widgets.yard_widget import YardWidget
from src.tui.widgets.fishing_widget import FishingWidget
from src.tui.widgets.shop_widget import ShopWidget
from src.tui.widgets.my_room_widget import MyRoomWidget
from src.tui.widgets.daily_widget import DailyWidget
from src.tui.widgets.leaderboard_widget import LeaderboardWidget


class MainMenuScreen(Screen):
    """Main menu screen with sidebar navigation and dynamic content."""

    current_section = reactive("job_center")
    user: User

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.user_repo = UserRepository()

    def compose(self) -> ComposeResult:
        # Sidebar with stats and navigation
        with Vertical(id="sidebar"):
            with Static(id="user-stats"):
                yield Label(f"👤 {self.user.nickname}")
                yield Label(f"🪙 {self.user.balance}", classes="currency")
                yield Label(f"⭐ {self.user.xp} XP", classes="xp")
                yield Label(f"🔼 Level {self.user.level}", classes="level")
                yield Label(f"📊 XP: {self.user.xp}/{self.user.xp_for_next_level()}")

            menu_items = [
                ("job_center", "💼 Job Center"),
                ("casino", "🎰 Casino"),
                ("yard", "🌾 Yard"),
                ("fishing", "🎣 Fishing"),
                ("my_room", "🏠 My Room"),
                ("shop", "🛒 Shop"),
                ("daily", "📅 Daily Rewards"),
                ("leaderboard", "🏆 Leaderboard"),
            ]

            with ListView(id="main-menu-list"):
                for section_id, label in menu_items:
                    yield ListItem(Label(label), id=f"menu-{section_id}")
                yield ListItem(Label("🚪 Logout"), id="menu-logout")

        # Dynamic content area
        with Vertical(id="content-area"):
            yield JobCenterWidget(self.user)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle menu selection."""
        item_id = event.item.id

        if item_id == "menu-logout":
            self.app.push_screen(LogoutConfirmScreen())
            return

        section = item_id.replace("menu-", "")
        self.current_section = section
        self._load_section(section)

    def _load_section(self, section: str):
        """Load the appropriate section widget."""
        content_area = self.query_one("#content-area", Vertical)
        content_area.remove_children()

        widgets = {
            "job_center": JobCenterWidget,
            "casino": CasinoWidget,
            "yard": YardWidget,
            "fishing": FishingWidget,
            "my_room": MyRoomWidget,
            "shop": ShopWidget,
            "daily": DailyWidget,
            "leaderboard": LeaderboardWidget,
        }

        widget_class = widgets.get(section, JobCenterWidget)
        content_area.mount(widget_class(self.user))

    def refresh_user_stats(self):
        """Refresh user stats display."""
        # Reload user from database
        fresh_user = self.user_repo.get_by_id(self.user.id)
        if fresh_user:
            self.user = fresh_user
            stats = self.query_one("#user-stats", Static)
            stats.update(
                f"👤 {self.user.nickname}\n"
                f"🪙 {self.user.balance}\n"
                f"⭐ {self.user.xp} XP\n"
                f"🔼 Level {self.user.level}\n"
                f"📊 XP: {self.user.xp}/{self.user.xp_for_next_level()}"
            )


class LogoutConfirmScreen(Screen):
    """Logout confirmation dialog."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label("🚪 Logout", classes="dialog-title")
            yield Static("Are you sure you want to logout?", classes="dialog-content")
            with Horizontal():
                yield Button("Yes", id="btn-yes", variant="error")
                yield Button("No", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-yes":
            self.app.current_user = None
            self.dismiss()
        else:
            self.dismiss()


from textual.widgets import Button
