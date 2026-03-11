"""Main TUI application using Textual."""

from __future__ import annotations

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive

from src.config.settings import get_settings, Settings
from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.db.sqlite_manager import get_db

from src.tui.screens.auth_screens import LoginScreen, RegisterScreen, WelcomeScreen
from src.tui.screens.main_menu_screen import MainMenuScreen
from src.tui.themes.default import DEFAULT_CSS


class HikikimoApp(App):
    """Main Hikikimo Life TUI application."""

    CSS = DEFAULT_CSS
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f1", "help", "Help", show=True),
        Binding("f5", "refresh", "Refresh", show=True),
    ]

    settings: Settings
    current_user: reactive[Optional[User]] = reactive(None)

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.user_repo = UserRepository()

    def compose(self) -> ComposeResult:
        """Compose the application."""
        yield WelcomeScreen()

    def on_mount(self):
        """Handle app mount."""
        self.title = "Hikikimo Life v2"
        self.sub_title = "Terminal Life Simulation"

    def watch_current_user(self, user: Optional[User]):
        """Watch for user changes and update UI."""
        if user is None:
            self.push_screen(WelcomeScreen())
        else:
            self.push_screen(MainMenuScreen(user))

    def action_help(self):
        """Show help screen."""
        from src.tui.screens.help_screen import HelpScreen
        self.push_screen(HelpScreen())

    def action_refresh(self):
        """Refresh current screen."""
        self.refresh()

    def on_user_logged_in(self, user: User):
        """Handle user login event."""
        self.current_user = user

    def on_user_logged_out(self):
        """Handle user logout event."""
        self.current_user = None


def run_app():
    """Entry point to run the TUI application."""
    app = HikikimoApp()
    app.run()


if __name__ == "__main__":
    run_app()
