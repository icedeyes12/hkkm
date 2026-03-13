"""Default theme and CSS for Hikikimo Life TUI.

Uses $primary-darken-2 (blue background) for visibility
instead of $surface (black background).
"""

DEFAULT_CSS = """
/* Base - visible container with blue background */
Screen {
    align: center middle;
}

/* Start Screen - use blue bg for visibility */
StartScreen {
    align: center middle;
}

StartScreen .welcome-container {
    width: 50;
    height: auto;
    background: $primary-darken-2;
    border: solid $primary;
    padding: 2;
}

StartScreen Static {
    color: $text;
    text-align: center;
}

StartScreen Label {
    color: $text-muted;
    text-align: center;
    margin: 1 0;
}

StartScreen Button {
    width: 100%;
    margin: 1 0;
}

/* Main Menu */
MainMenuScreen {
    layout: horizontal;
}

#sidebar {
    width: 28;
    dock: left;
    background: $surface-darken-1;
    border-right: solid $border;
}

#user-stats {
    height: auto;
    background: $primary;
    padding: 1;
    color: $text;
}

#content-area {
    width: 1fr;
    background: $background;
    padding: 1;
}

/* Common */
.section-title {
    text-style: bold;
    text-align: center;
    color: $accent;
    margin: 1 0;
}

.currency { color: $warning; text-style: bold; }
.xp { color: $success; }
.level { color: $primary; }
.warning { color: $error; }
"""
