"""Default theme and CSS for Hikikimo Life TUI."""

DEFAULT_CSS = """
/* Base - ensure visible text */
Screen {
    align: center middle;
    background: $surface;
}

Static, Label {
    color: $text;
}

/* Start Screen */
StartScreen {
    align: center middle;
}

StartScreen .welcome-container {
    width: 50;
    height: auto;
    background: $surface;
    border: solid $primary;
    padding: 2;
}

StartScreen .banner {
    text-align: center;
    text-style: bold;
    color: $text;
    margin-bottom: 1;
}

StartScreen .subtitle {
    text-align: center;
    color: $text-muted;
    margin-bottom: 2;
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
    background: $primary-darken-2;
    padding: 1;
    border-bottom: solid $border;
}

#user-stats Static {
    margin: 0 0 1 0;
}

#content-area {
    width: 1fr;
    background: $background;
    padding: 1;
}

ListView:focus {
    background: $primary-darken-2;
}

ListItem:focus {
    background: $primary;
}

/* Widgets */
JobCenterWidget, CasinoWidget, YardWidget, ShopWidget {
    padding: 1;
}

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
