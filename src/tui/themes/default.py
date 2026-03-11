"""Default theme and CSS for Hikikimo Life TUI."""

DEFAULT_CSS = """
/* Base styles */
Screen {
    align: center middle;
}

/* Header styling */
Header {
    background: $primary;
    color: $text;
    height: 3;
    dock: top;
}

HeaderTitle {
    content-align: center middle;
    text-style: bold;
}

/* Footer styling */
Footer {
    background: $surface;
    color: $text;
    height: 1;
    dock: bottom;
}

/* Common widget styles */
.section-title {
    text-style: bold;
    text-align: center;
    color: $accent;
    margin: 1 0;
}

.currency {
    color: $warning;
    text-style: bold;
}

.xp {
    color: $success;
}

.level {
    color: $primary;
}

.warning {
    color: $error;
}

/* Start Screen */
StartScreen {
    align: center middle;
}

StartScreen Vertical {
    width: auto;
    height: auto;
    align: center middle;
}

StartScreen .banner {
    color: $accent;
    text-align: center;
    margin-bottom: 2;
}

StartScreen .subtitle {
    color: $text-muted;
    text-align: center;
    margin-bottom: 3;
}

StartScreen Button {
    width: 30;
    margin: 1 0;
}

/* Main Menu Screen */
MainMenuScreen {
    layout: horizontal;
}

#sidebar {
    width: 28;
    dock: left;
    background: $surface;
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

#main-menu-list {
    height: 1fr;
}

#content-area {
    width: 1fr;
    background: $background;
    padding: 1;
}

ListView:focus {
    background: $primary-darken-2;
}

ListItem {
    padding: 1;
}

ListItem:focus {
    background: $primary;
}

/* Job Center Widget */
JobCenterWidget {
    padding: 1;
}

#job-grid {
    grid-size: 3;
    grid-gutter: 1;
}

.job-card {
    background: $surface;
    border: solid $border;
    padding: 1;
    height: auto;
}

.job-card:focus-within {
    border: solid $primary;
}

.job-card .title {
    text-style: bold;
    text-align: center;
    color: $accent;
    margin-bottom: 1;
}

.job-card .description {
    color: $text-muted;
    text-align: center;
    margin-bottom: 1;
}

/* Casino Widget */
CasinoWidget {
    padding: 1;
}

.casino-game {
    background: $surface;
    border: solid $border;
    padding: 2;
    margin: 1;
}

/* Yard Widget */
YardWidget {
    padding: 1;
}

.plot-grid {
    grid-size: 3;
    grid-gutter: 1;
}

.plot {
    background: $surface;
    border: solid $border;
    padding: 1;
    height: 8;
}

.plot.empty {
    color: $text-muted;
}

.plot.growing {
    border: solid $warning;
}

.plot.ready {
    border: solid $success;
}

.plot.withered {
    border: solid $error;
    color: $text-muted;
}

.barn-grid {
    grid-size: 2;
    grid-gutter: 1;
}

.barn-slot {
    background: $surface;
    border: solid $border;
    padding: 1;
    height: auto;
}

/* Shop Widget */
ShopWidget {
    padding: 1;
}

.shop-tabs {
    height: 3;
    dock: top;
}

.shop-content {
    height: 1fr;
}

.shop-item {
    layout: horizontal;
    height: 3;
    background: $surface;
    border-bottom: solid $border;
    padding: 0 1;
}

.shop-item-name {
    width: 1fr;
    content-align: center middle;
}

.shop-item-price {
    width: 10;
    content-align: right middle;
    color: $warning;
}

.shop-item-button {
    width: 8;
}

/* Dialog styles */
.dialog {
    background: $surface;
    border: solid $primary;
    padding: 2;
    width: 50;
    height: auto;
}

.dialog-title {
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

.dialog-content {
    text-align: center;
    margin: 1 0;
}

/* Progress bars */
ProgressBar {
    height: 1;
    margin: 1 0;
}

/* DataTable styling */
DataTable {
    height: 1fr;
    border: solid $border;
}

DataTable > .datatable--header {
    background: $primary;
    color: $text;
    text-style: bold;
}

/* Help Screen */
HelpScreen {
    align: center middle;
}

.help-container {
    width: 70;
    height: auto;
    max-height: 40;
    background: $surface;
    border: solid $primary;
    padding: 2;
}

.help-content {
    height: 1fr;
    overflow-y: auto;
}

/* Notification/Toast styles */
.toast-success {
    background: $success;
    color: $text;
}

.toast-error {
    background: $error;
    color: $text;
}

.toast-warning {
    background: $warning;
    color: $text;
}

.toast-info {
    background: $primary;
    color: $text;
}
"""
