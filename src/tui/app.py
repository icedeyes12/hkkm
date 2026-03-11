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
from src.db.sqlite_manager import get_db
from src.tui.screens.main_menu_screen import MainMenuScreen
from src.tui.themes.default import DEFAULT_CSS


class StartScreen(Screen):
    """Simple start screen - no auth needed."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="welcome-container"):
            yield Static("""
╔═══════════════════════════════════════╗
║     🎮 HIKIKIMO LIFE v2 🎮            ║
║                                       ║
║   Terminal Life Simulation Game       ║
╚═══════════════════════════════════════╝
            "", classes="banner")
            yield Label("A chill life sim in your terminal", classes="subtitle")
            yield Button("▶ Start Game", id="btn-start", variant="primary")
            yield Button("🗑 New Game (reset)", id="btn-reset", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start":
            self.app.start_game()
        elif event.button.id == "btn-reset":
            self.app.reset_game()


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
        yield StartScreen()

    def on_mount(self):
        self.title = "Hikikimo Life v2"
        self.sub_title = "Single Player"

    def start_game(self):
        """Load or create single player save."""
        # Try to load existing player
        self.player = self.user_repo.get_single_player()
        
        if self.player is None:
            # Create new player
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
