"""My Room widget for user profile and settings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from src.core.models.user import User
from src.core.repositories.inventory_repository import InventoryRepository
from src.core.repositories.user_repository import UserRepository


class MyRoomWidget(Static):
    """My Room section for profile and settings."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.user_repo = UserRepository()
        self.inventory_repo = InventoryRepository()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🏠 My Room", classes="section-title")

            yield Label("👤 Profile")
            yield Static(f"Username: {self.user.username}")
            yield Static(f"Nickname: {self.user.nickname}")
            yield Static(f"Level: {self.user.level}")
            yield Static(f"XP: {self.user.xp} / {self.user.xp_for_next_level()}")
            yield Static(f"Balance: {self.user.balance} 🪙")

            yield Label("📊 Stats")
            yield Static(f"Account created: {self.user.created_at.strftime('%Y-%m-%d')}")
            if self.user.last_login:
                yield Static(f"Last login: {self.user.last_login.strftime('%Y-%m-%d %H:%M')}")

            yield Label("🎒 Quick Inventory")
            inventory = self.inventory_repo.get_user_inventory(self.user.id)
            if inventory:
                total_items = sum(item.quantity for item in inventory)
                yield Static(f"Total items: {total_items}")
            else:
                yield Static("No items yet!")

            yield Label("⚙️ Settings")
            yield Label("Change Nickname:")
            with Horizontal():
                yield Input(value=self.user.nickname, id="nickname-input", placeholder="New nickname")
                yield Button("Update", id="btn-update-nickname")

            yield Static("", id="settings-result")

            yield Label("🔓 Test Mode")
            with Horizontal():
                yield Button("Enable Test Mode", id="btn-test", variant="warning")
                yield Button("Reset Account", id="btn-reset", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        result = self.query_one("#settings-result", Static)

        if btn_id == "btn-update-nickname":
            new_nick = self.query_one("#nickname-input", Input).value.strip()
            if new_nick and len(new_nick) <= 20:
                self.user.nickname = new_nick
                self.user_repo.update(self.user)
                result.update("✅ Nickname updated!")
                self._refresh_stats()
            else:
                result.update("❌ Invalid nickname")

        elif btn_id == "btn-test":
            result.update("🔓 Test mode enabled! Cheat commands available.")
            self.app.notify("Test mode enabled - use 'titit' or '𓂸' for cheats")

        elif btn_id == "btn-reset":
            result.update("⚠️ This would reset your account (not implemented for safety)")

    def _refresh_stats(self):
        """Refresh parent stats."""
        try:
            parent = self.parent
            if parent and hasattr(parent, "refresh_user_stats"):
                parent.refresh_user_stats()
        except:
            pass
