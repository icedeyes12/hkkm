#!/usr/bin/env python3
"""Minimal test - bare bones Textual app."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Label, Static

class TestApp(App):
    """Minimal test app."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    Vertical {
        width: 40;
        height: auto;
        border: solid green;
        padding: 2;
        background: $surface;
    }
    Static {
        text-align: center;
        color: $text;
    }
    Button {
        width: 100%;
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("🎮 HIKIKIMO LIFE 🎮\n\nMinimal Test")
            yield Button("Click Me", variant="primary")
            yield Label("If you see this, CSS works!")

    def on_button_pressed(self) -> None:
        self.exit("Button clicked!")

if __name__ == "__main__":
    app = TestApp()
    result = app.run()
    print(f"Result: {result}")
