"""Help screen with keyboard shortcuts and instructions."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, Static


class HelpScreen(Screen):
    """Help screen with controls and instructions."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="help-container"):
            yield Label("❓ Help & Controls", classes="dialog-title")

            with Vertical(classes="help-content"):
                yield Label("🎮 Navigation")
                yield Static("• Tab / Shift+Tab - Move between elements")
                yield Static("• ↑ / ↓ / ← / → - Navigate menus")
                yield Static("• Enter - Select / Confirm")
                yield Static("• Esc / q - Back / Cancel")

                yield Label("🎯 Game Sections")
                yield Static("• Job Center - Work, trade, or commit crimes for coins")
                yield Static("• Casino - Gamble your coins (high risk!)")
                yield Static("• Yard - Farm crops and raise animals")
                yield Static("• Fishing - Catch fish for profit")
                yield Static("• Shop - Buy tools, rods, seeds, and feed")
                yield Static("• Daily - Claim daily rewards")
                yield Static("• Leaderboard - See top players")

                yield Label("💡 Tips")
                yield Static("• Higher level = better rewards")
                yield Static("• Farm crops need regular watering")
                yield Static("• Feed animals to keep them happy")
                yield Static("• Different fishing locations have different fish")
                yield Static("• Save often - auto-save every 5 minutes")

                yield Label("⌨️ Shortcuts")
                yield Static("• F1 - This help screen")
                yield Static("• F5 - Refresh current screen")
                yield Static("• Ctrl+Q - Quit application")

            yield Button("Close", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle close button."""
        if event.button.id == "btn-close":
            self.dismiss()
