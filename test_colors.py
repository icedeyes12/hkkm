#!/usr/bin/env python3
"""Color diagnostic test for Textual.

This test displays all color variables to identify
which ones provide visible contrast in dark mode.
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Label, Button
from textual.containers import Vertical, Grid


class ColorTest(App):
    """Display all Textual color variables."""

    CSS = """
    Screen {
        align: center middle;
    }
    
    #test-grid {
        grid-size: 3;
        grid-gutter: 1;
        width: 80;
        height: auto;
    }
    
    .color-box {
        height: 3;
        padding: 1;
        text-align: center;
    }
    
    /* Test background colors */
    .bg-surface { background: $surface; }
    .bg-surface-darken-1 { background: $surface-darken-1; }
    .bg-surface-darken-2 { background: $surface-darken-2; }
    .bg-background { background: $background; }
    .bg-primary { background: $primary; }
    .bg-primary-darken-2 { background: $primary-darken-2; }
    .bg-accent { background: $accent; }
    .bg-success { background: $success; }
    .bg-warning { background: $warning; }
    .bg-error { background: $error; }
    
    /* Test text colors */
    .text-text { color: $text; }
    .text-text-muted { color: $text-muted; }
    .text-primary { color: $primary; }
    .text-accent { color: $accent; }
    .text-success { color: $success; }
    .text-warning { color: $warning; }
    .text-error { color: $error; }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🎨 TEXTUAL COLOR TEST", classes="text-text")
            yield Label("Dark mode color variable visibility test\n")
            
            with Grid(id="test-grid"):
                # Background color tests with $text on top
                yield Static("$surface\n$text", classes="color-box bg-surface text-text")
                yield Static("$surface-darken-1\n$text", classes="color-box bg-surface-darken-1 text-text")
                yield Static("$surface-darken-2\n$text", classes="color-box bg-surface-darken-2 text-text")
                
                yield Static("$background\n$text", classes="color-box bg-background text-text")
                yield Static("$primary\n$text", classes="color-box bg-primary text-text")
                yield Static("$primary-darken-2\n$text", classes="color-box bg-primary-darken-2 text-text")
                
                yield Static("$accent\n$text", classes="color-box bg-accent text-text")
                yield Static("$success\n$text", classes="color-box bg-success text-text")
                yield Static("$warning\n$text", classes="color-box bg-warning text-text")
            
            yield Label("\nButtons with variants:")
            yield Button("variant=primary", variant="primary")
            yield Button("variant=error", variant="error")
            yield Button("variant=success", variant="success")
            
            yield Label("\nPress Ctrl+C to exit", classes="text-muted")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        self.notify(f"Clicked: {event.button.label}")


if __name__ == "__main__":
    app = ColorTest()
    app.run()
