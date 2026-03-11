"""Main TUI application - Single player, no auth."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Label, Static
from textual.containers import Vertical

from src.config.settings import get_settings
from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.tui.screens.main_menu_screen import MainMenuScreen
from src.tui.themes.default import DEFAULT_CSS


class StartScreen(Screen):
    """Simple start screen - no auth needed."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="welcome-container"):
            yield Static(
                "\n╔═══════════════════════════════════════╗\n"
                "║     🎮 HIKIKIMO LIFE v2 🎮            ║\n"
                "║                                       ║\n"
                "║   Terminal Life Simulation Game       ║\n"
                "╚═══════════════════════════════════════╝\n",
                classes="banner"
            )
            yield Label("A chill life sim in your terminal", classes="subtitle")
            yield Button("▶ Start Game", id="btn-start", variant="primary")
            yield Button("🗑 New Game (reset)", id="btn-reset", variant="error")


class HikikimoApp(App):
    """Single-player Hikikimo Life - no auth, no leaderboard."""

    CSS = DEFAULT_CSS
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f1", "help", "Help", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self.player: User | None = None

    def compose(self) -> ComposeResult:
        print("DEBUG: App composed")
        yield StartScreen()

    def on_mount(self):
        print(">>> APP MOUNTED <<<")
        self.title = "Hikikimo Life v2"
        self.sub_title = "Single Player"

    def start_game(self):
        """Load or create single player save."""
        print("DEBUG: start_game is being called")
        self.player = self.user_repo.get_single_player()
        if self.player is None:
            self.player = User.create_single_player()
            self.user_repo.save_single_player(self.player)
        self.push_screen(MainMenuScreen(self.player))

    def reset_game(self):
        """Reset all progress."""
        self.user_repo.delete_single_player()
        self.start_game()

    def action_help(self):
        from src.tui.screens.help_screen import HelpScreen
        self.push_screen(HelpScreen())


def run_app():
    app = HikikimoApp()
    app.run()


if __name__ == "__main__":
    run_app()
