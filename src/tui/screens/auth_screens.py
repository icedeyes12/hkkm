"""Authentication screens (Welcome, Login, Register)."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static

from src.core.exceptions import ValidationError
from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.utils.validators import validate_username, validate_password


class WelcomeScreen(Screen):
    """Welcome screen with login/register options."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="welcome-container"):
            yield Static(
                """
╔═══════════════════════════════════════╗
║     🎮 HIKIKIMO LIFE v2 🎮            ║
║                                       ║
║   Terminal Life Simulation Game       ║
║                                       ║
╚═══════════════════════════════════════╝
""",
                classes="banner",
            )
            yield Label("Welcome! Please choose an option:", classes="section-title")
            with Horizontal(classes="button-row"):
                yield Button("🔐 Login", id="btn-login", variant="primary")
                yield Button("📝 Register", id="btn-register")
                yield Button("👤 Guest", id="btn-guest")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-login":
            self.app.push_screen(LoginScreen())
        elif event.button.id == "btn-register":
            self.app.push_screen(RegisterScreen())
        elif event.button.id == "btn-guest":
            # Create guest user directly
            guest = User.create_guest()
            self.app.post_message(UserLoggedIn(guest))


class LoginScreen(Screen):
    """Login screen for existing users."""

    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()

    def compose(self) -> ComposeResult:
        with Vertical(classes="auth-container"):
            yield Label("🔐 Login", classes="section-title")
            yield Label("Username:")
            yield Input(placeholder="Enter username", id="input-username")
            yield Label("Password:")
            yield Input(
                placeholder="Enter password",
                password=True,
                id="input-password",
            )
            yield Label("", id="error-message", classes="warning")
            with Horizontal():
                yield Button("Login", id="btn-submit", variant="primary")
                yield Button("Back", id="btn-back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-back":
            self.app.pop_screen()
            return

        if event.button.id == "btn-submit":
            self._attempt_login()

    def _attempt_login(self):
        """Attempt to log in user."""
        username = self.query_one("#input-username", Input).value.strip()
        password = self.query_one("#input-password", Input).value
        error_label = self.query_one("#error-message", Label)

        if not username or not password:
            error_label.update("❌ Please enter username and password")
            return

        try:
            user = self.user_repo.get_by_username(username)
            if user and user.verify_password(password):
                user.last_login = datetime.now()
                self.user_repo.update(user)
                self.app.post_message(UserLoggedIn(user))
                self.dismiss()
            else:
                error_label.update("❌ Invalid username or password")
        except Exception as e:
            error_label.update(f"❌ Error: {str(e)}")


class RegisterScreen(Screen):
    """Registration screen for new users."""

    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()

    def compose(self) -> ComposeResult:
        with Vertical(classes="auth-container"):
            yield Label("📝 Register", classes="section-title")
            yield Label("Username (3-20 chars, alphanumeric):")
            yield Input(placeholder="Choose username", id="input-username")
            yield Label("Nickname (display name):")
            yield Input(placeholder="Choose nickname", id="input-nickname")
            yield Label("Password (min 6 chars):")
            yield Input(
                placeholder="Choose password",
                password=True,
                id="input-password",
            )
            yield Label("Confirm Password:")
            yield Input(
                placeholder="Confirm password",
                password=True,
                id="input-confirm",
            )
            yield Label("", id="error-message", classes="warning")
            with Horizontal():
                yield Button("Register", id="btn-submit", variant="primary")
                yield Button("Back", id="btn-back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-back":
            self.app.pop_screen()
            return

        if event.button.id == "btn-submit":
            self._attempt_register()

    def _attempt_register(self):
        """Attempt to register new user."""
        username = self.query_one("#input-username", Input).value.strip()
        nickname = self.query_one("#input-nickname", Input).value.strip()
        password = self.query_one("#input-password", Input).value
        confirm = self.query_one("#input-confirm", Input).value
        error_label = self.query_one("#error-message", Label)

        # Validation
        if not username or not nickname or not password:
            error_label.update("❌ Please fill in all fields")
            return

        if password != confirm:
            error_label.update("❌ Passwords do not match")
            return

        try:
            validate_username(username)
            validate_password(password)
        except ValidationError as e:
            error_label.update(f"❌ {str(e)}")
            return

        # Check if username exists
        if self.user_repo.get_by_username(username):
            error_label.update("❌ Username already taken")
            return

        try:
            user = self.user_repo.create(
                username=username,
                password=password,
                nickname=nickname,
            )
            self.app.post_message(UserLoggedIn(user))
            self.dismiss()
        except Exception as e:
            error_label.update(f"❌ Error: {str(e)}")


# Events
from datetime import datetime


class UserLoggedIn:
    """Event emitted when user logs in."""

    def __init__(self, user: User):
        self.user = user
