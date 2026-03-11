# 🎮 Hikikimo Life — TUI Modernization Roadmap

**Project:** hkkm (Hikikimo Life)  
**Target:** Full Terminal User Interface (TUI) with SQLite backend  
**Primary Platform:** Termux (Android) — Cross-platform: Windows, Linux, macOS  
**Language:** Python 3.12.x  

---

## 📋 Executive Summary

This roadmap transforms the current CLI-based life simulation game into a rich, keyboard-driven TUI application with a modular architecture, SQLite persistence, and cross-platform terminal compatibility. The migration follows a strict hierarchical breakdown: **Phase → Task → Sub-task → Micro-task → Nano-task**, with comprehensive edge case simulations for each major component.

---

# 🗺️ PHASE 1: Foundation & Architecture Setup

## Task 1.1: Project Structure Reorganization

### Sub-task 1.1.1: Directory Architecture Design
**Objective:** Establish clean separation of concerns with MVC-inspired structure.

#### Micro-task 1.1.1.1: Create Base Directory Structure
```
hkkm_v2/
├── src/
│   ├── __init__.py
│   ├── core/                    # Business logic (pure Python, no UI)
│   │   ├── __init__.py
│   │   ├── models/            # Data models (dataclasses)
│   │   ├── services/          # Business logic services
│   │   ├── repositories/    # Database abstraction layer
│   │   └── exceptions/        # Custom exception classes
│   ├── tui/                     # Terminal UI layer
│   │   ├── __init__.py
│   │   ├── app.py             # Main TUI application container
│   │   ├── screens/           # Screen components (one per major menu)
│   │   ├── widgets/           # Reusable UI components
│   │   ├── themes/            # Color schemes & styling
│   │   └── utils/             # TUI helpers (terminal detection, etc.)
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   ├── sqlite_manager.py  # Connection pooling & migrations
│   │   ├── migrations/        # Version-controlled schema changes
│   │   └── seed_data/         # Initial game data (JSON → SQLite import)
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py        # Pydantic settings with env var support
│   │   └── platform.py        # Platform detection & capabilities
│   └── utils/                   # Shared utilities
│       ├── __init__.py
│       ├── path_helper.py     # Cross-platform path handling
│       ├── encoding.py        # Unicode & encoding utilities
│       └── validators.py      # Input validation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                   # Terminal emulation tests
├── assets/
│   └── ascii_art/             # Game banners & decorations
├── scripts/
│   ├── migrate_data.py        # JSON → SQLite migration
│   └── setup_termux.py        # Termux-specific setup
├── pyproject.toml             # Modern Python packaging
└── README_V2.md
```

**Nano-task 1.1.1.1.1:** Create `src/` with `__init__.py` exports  
**Nano-task 1.1.1.1.2:** Create `tests/` directory with `pytest.ini`  
**Nano-task 1.1.1.1.3:** Set up `pyproject.toml` with dependencies  
**Nano-task 1.1.1.1.4:** Create `.gitignore` for Python + Termux specifics

#### Micro-task 1.1.1.2: Dependency Management Setup

**Nano-task 1.1.1.2.1:** Define `pyproject.toml` dependencies:
```toml
[project]
name = "hkkm"
version = "2.0.0"
requires-python = ">=3.12"
dependencies = [
    "textual>=0.50.0",          # TUI framework (primary)
    "sqlite3-utils>=3.35",      # SQLite helpers
    "pydantic>=2.5",            # Data validation
    "pydantic-settings>=2.1",   # Configuration management
    "rich>=13.7",               # Rich text rendering (used by Textual)
    "platformdirs>=4.0",        # Cross-platform directories
    "click>=8.1",               # CLI entry points
    "structlog>=24.1",          # Structured logging
    "typing-extensions>=4.9",   # Extended type hints
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.1",
    "black>=23.12",
    "ruff>=0.1.9",
    "mypy>=1.7",
    "freezegun>=1.4",           # Time mocking for tests
]
```

**Nano-task 1.1.1.2.2:** Create `requirements-lock.txt` for reproducible builds  
**Nano-task 1.1.1.2.3:** Set up virtual environment automation script

### Sub-task 1.1.2: Configuration System Architecture

#### Micro-task 1.1.2.1: Platform Detection Module

**Nano-task 1.1.2.1.1:** Implement `src/config/platform.py`:
```python
from enum import Enum, auto
import os
import sys

class Platform(Enum):
   TERMUX = auto()
    WINDOWS_CMD = auto()
    WINDOWS_POWERSHELL = auto()
    LINUX = auto()
    MACOS = auto()
    WSL = auto()
    UNKNOWN = auto()

class TerminalCapabilities:
    """Detect terminal features for adaptive rendering."""
    supports_unicode: bool
    supports_truecolor: bool
    supports_256_color: bool
    max_colors: int
    has_mouse_support: bool
    preferred_encoding: str

class PlatformDetector:
    @staticmethod
    def detect() -> Platform:
        # Termux detection: check for $PREFIX or /data/data/com.termux
        # Windows: sys.platform == 'win32'
        # WSL: /proc/version contains 'microsoft'
        # etc.
        ...
    
    @staticmethod
    def get_terminal_capabilities() -> TerminalCapabilities:
        # Use curses or environment variables to detect
        ...
```

**Nano-task 1.1.2.1.2:** Create comprehensive platform test matrix  
**Nano-task 1.1.2.1.3:** Document platform-specific quirks

#### Micro-task 1.1.2.2: Settings Management with Pydantic

**Nano-task 1.1.2.2.1:** Define `src/config/settings.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, DirectoryPath
from pathlib import Path

class DatabaseSettings(BaseSettings):
    url: str = Field(default="sqlite:///hkkm.db")
    echo: bool = Field(default=False)  # SQL logging
    pool_size: int = Field(default=5)
    
class TUISettings(BaseSettings):
    theme: str = Field(default="default")
    animation_speed: float = Field(default=1.0)
    enable_mouse: bool = Field(default=True)
    vim_mode: bool = Field(default=False)
    
class GameSettings(BaseSettings):
    starting_balance: int = Field(default=500)
    max_level: int = Field(default=15)
    auto_save_interval: int = Field(default=300)  # seconds

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__'
    )
    
    app_name: str = "Hikikimo Life"
    debug: bool = Field(default=False)
    data_dir: DirectoryPath = Field(default_factory=lambda: Path.home() / ".hkkm")
    
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    tui: TUISettings = Field(default_factory=TUISettings)
    game: GameSettings = Field(default_factory=GameSettings)
```

### Sub-task 1.1.3: Data Migration Strategy (JSON → SQLite)

#### Micro-task 1.1.3.1: Schema Design

**Nano-task 1.1.3.1.1:** Design normalized database schema:
```sql
-- Users table (replaces users.json)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    nickname TEXT NOT NULL,
    password_hash TEXT NOT NULL,  -- Upgraded from simple SHA256
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    balance INTEGER DEFAULT 500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_guest BOOLEAN DEFAULT FALSE,
    unlocked_features JSON  -- Store as JSON for flexibility
);

-- Inventory table (normalized, replaces nested inventory dict)
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_type TEXT NOT NULL,  -- 'tools', 'rods', 'baits', 'seeds', 'feeds', 'fish', 'crops', 'products'
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, item_type, item_id)
);

-- Field plots table (new: track farming state)
CREATE TABLE field_plots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    plot_number INTEGER NOT NULL,
    crop_id INTEGER,
    planted_at TIMESTAMP,
    last_watered TIMESTAMP,
    growth_stage INTEGER DEFAULT 0,  -- 0=empty, 1=seed, 2=growing, 3=ready, 4=withered
    health INTEGER DEFAULT 100,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, plot_number)
);

-- Barn slots table (new: track animals)
CREATE TABLE barn_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    slot_number INTEGER NOT NULL,
    animal_id INTEGER,
    acquired_at TIMESTAMP,
    last_fed TIMESTAMP,
    happiness INTEGER DEFAULT 50,
    product_ready_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, slot_number)
);

-- Game data tables (static, seeded from JSON)
CREATE TABLE fish (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    rarity TEXT NOT NULL,  -- 'common', 'uncommon', 'rare', 'legendary'
    base_price INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    min_weight REAL,
    max_weight REAL,
    habitat TEXT NOT NULL  -- 'pond', 'river', 'lake', 'ocean'
);

CREATE TABLE crops (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    growth_time INTEGER NOT NULL,  -- seconds
    delay_time INTEGER NOT NULL,   -- seconds
    base_price INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL
);

CREATE TABLE seeds (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    crop_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);

CREATE TABLE animals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE animal_products (
    id INTEGER PRIMARY KEY,
    animal_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    base_price INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    is_optional BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (animal_id) REFERENCES animals(id)
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,  -- 'tool', 'rod', 'bait', 'seed', 'feed'
    name TEXT NOT NULL,
    price INTEGER,
    -- Type-specific attributes stored as JSON
    attributes JSON
);

-- Leaderboard table
CREATE TABLE leaderboard (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    xp INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    rank_xp INTEGER,
    rank_wealth INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Activity log for debugging/audit
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Nano-task 1.1.3.1.2:** Create Entity-Relationship diagram  
**Nano-task 1.1.3.1.3:** Define indexes for query optimization

#### Micro-task 1.1.3.2: Migration Script Implementation

**Nano-task 1.1.3.2.1:** Create `scripts/migrate_data.py` with idempotent migration logic  
**Nano-task 1.1.3.2.2:** Implement data validation during migration  
**Nano-task 1.1.3.2.3:** Create rollback mechanism for failed migrations  
**Nano-task 1.1.3.2.4:** Add migration version tracking table

---

## Task 1.2: Database Layer Implementation

### Sub-task 1.2.1: SQLite Connection Management

#### Micro-task 1.2.1.1: Connection Pool & Thread Safety

**Nano-task 1.2.1.1.1:** Implement `src/db/sqlite_manager.py` with connection pooling:
```python
import sqlite3
from contextlib import contextmanager
from threading import Lock
from typing import Generator

class SQLiteManager:
    """Thread-safe SQLite connection manager with WAL mode support."""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self._pool_size = pool_size
        self._pool: list[sqlite3.Connection] = []
        self._lock = Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Enable WAL mode for better concurrency."""
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=30000000000")
    
    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool."""
        conn = None
        try:
            with self._lock:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    conn = sqlite3.connect(
                        self.db_path,
                        check_same_thread=False,
                        timeout=30.0,  # Wait up to 30s for locks
                        isolation_level=None  # Autocommit mode for explicit control
                    )
                    conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                with self._lock:
                    if len(self._pool) < self._pool_size:
                        self._pool.append(conn)
                    else:
                        conn.close()
    
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Execute within a transaction with automatic rollback on error."""
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
```

**Nano-task 1.2.1.1.2:** Implement retry logic for `database is locked` errors  
**Nano-task 1.2.1.1.3:** Add connection health checking  
**Nano-task 1.2.1.1.4:** Create database integrity verification function

#### Micro-task 1.2.1.2: Migration System

**Nano-task 1.2.1.2.1:** Create migration file naming convention: `YYYYMMDDHHMMSS_description.sql`  
**Nano-task 1.2.1.2.2:** Implement migration runner with versioning  
**Nano-task 1.2.1.2.3:** Create initial migration: `20250101000000_initial_schema.sql`  
**Nano-task 1.2.1.2.4:** Create seed data migration: `20250101000001_seed_game_data.sql`

### Sub-task 1.2.2: Repository Pattern Implementation

#### Micro-task 1.2.2.1: Base Repository

**Nano-task 1.2.2.1.1:** Implement `src/core/repositories/base.py`:
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from dataclasses import dataclass

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(ABC, Generic[T, ID]):
    """Base repository interface."""
    
    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[T]: ...
    
    @abstractmethod
    def get_all(self) -> List[T]: ...
    
    @abstractmethod
    def create(self, entity: T) -> T: ...
    
    @abstractmethod
    def update(self, entity: T) -> T: ...
    
    @abstractmethod
    def delete(self, id: ID) -> bool: ...
```

**Nano-task 1.2.2.1.2:** Create SQL query builder helper  
**Nano-task 1.2.2.1.3:** Implement pagination support

#### Micro-task 1.2.2.2: Concrete Repositories

**Nano-task 1.2.2.2.1:** Implement `UserRepository` with password hashing upgrade (bcrypt/argon2)  
**Nano-task 1.2.2.2.2:** Implement `InventoryRepository` with bulk operations  
**Nano-task 1.2.2.2.3:** Implement `FieldPlotRepository` for farming state  
**Nano-task 1.2.2.2.4:** Implement `BarnSlotRepository` for animal state  
**Nano-task 1.2.2.2.5:** Implement `LeaderboardRepository` with rank calculation  
**Nano-task 1.2.2.2.6:** Implement `GameDataRepository` for static game data

---

## 🔧 EDGE CASE SIMULATION — Phase 1

### Edge Case 1.1: Database Locking Scenarios

**Scenario:** Two TUI instances (or TUI + migration script) access database simultaneously.

| Condition | Probability | Mitigation Strategy |
|-----------|-------------|---------------------|
| Concurrent read | High | WAL mode allows concurrent reads |
| Read + Write | Medium | WAL mode, retry with exponential backoff |
| Write + Write | Low | Immediate transaction mode, 30s timeout |
| Long-running transaction | Medium | Transaction splitting, progress indicators |

**Mitigation Implementation:**
```python
import time
import random
from functools import wraps

def with_retry(max_attempts: int = 5, base_delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "database is locked" not in str(e) or attempt == max_attempts - 1:
                        raise
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

### Edge Case 1.2: Cross-Platform Path Handling

**Scenario:** Windows paths (`C:\Users\name\.hkkm\data.db`) vs Unix paths (`/home/name/.hkkm/data.db`).

**Simulation Matrix:**

| Platform | Data Directory | Special Handling |
|----------|----------------|------------------|
| Termux | `/data/data/com.termux/files/home/.hkkm` | Check $PREFIX, handle Android storage permissions |
| Windows CMD | `%USERPROFILE%\.hkkm` | Expand env vars, handle spaces in usernames |
| Windows PowerShell | `$env:USERPROFILE\.hkkm` | Same as CMD |
| WSL | `/home/username/.hkkm` OR Windows path | Detect WSL, prefer Linux paths |
| Linux | `~/.hkkm` or `$XDG_DATA_HOME/hkkm` | Follow XDG spec if available |
| macOS | `~/Library/Application Support/hkkm` | Use macOS conventions |

**Implementation:**
```python
from pathlib import Path
import platformdirs

def get_data_directory() -> Path:
    """Get platform-appropriate data directory."""
    # Use platformdirs for standard locations
    data_dir = platformdirs.user_data_dir("hkkm", "hkkm_project")
    
    # Termux override
    if 'TERMUX_VERSION' in os.environ:
        termux_home = Path(os.environ.get('HOME', '/data/data/com.termux/files/home'))
        data_dir = termux_home / '.hkkm'
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
```

### Edge Case 1.3: Encoding & Character Issues

**Scenario:** Unicode characters (🪙, emoji, box-drawing) display incorrectly on different terminals.

**Simulation Results:**

| Terminal | Unicode Support | Color Support | Special Handling |
|----------|-----------------|---------------|------------------|
| Termux | Full | Truecolor | None |
| Windows CMD | Limited | 16 colors | Fallback to ASCII art |
| Windows PowerShell | Good | 256 colors | Detect version, use appropriate chars |
| Windows Terminal | Full | Truecolor | None |
| Linux (modern) | Full | Truecolor | None |
| macOS Terminal | Full | 256 colors | None |
| macOS iTerm2 | Full | Truecolor | None |

**Mitigation Strategy:**
```python
class EncodingManager:
    ASCII_FALLBACKS = {
        '🪙': '$',
        '⭐': '*',
        '🔼': '^',
        '♨️': '~',
        '👤': '@',
        '█': '#',
        '░': '-',
        '═': '=',
        '║': '|',
        '╔': '+',
        '╗': '+',
        '╚': '+',
        '╝': '+',
    }
    
    def __init__(self, capabilities: TerminalCapabilities):
        self.use_unicode = capabilities.supports_unicode
        self.encoding = capabilities.preferred_encoding or 'utf-8'
    
    def encode_text(self, text: str) -> str:
        if self.use_unicode:
            return text
        # Replace unicode with ASCII fallbacks
        for unicode_char, ascii_char in self.ASCII_FALLBACKS.items():
            text = text.replace(unicode_char, ascii_char)
        return text
```

---

# 🗺️ PHASE 2: TUI Framework Integration & Core UI Architecture

## Task 2.1: TUI Framework Selection & Setup

### Sub-task 2.1.1: Textual Framework Integration

#### Micro-task 2.1.1.1: Framework Evaluation & Selection

**Decision Rationale:**
- **Selected:** [Textual](https://textual.textualize.io/) — Modern Python TUI framework with:
  - Reactive data model (React-like)
  - CSS-like styling system
  - Built-in widgets (DataTable, Tree, Input, Button, etc.)
  - Keyboard & mouse support
  - Cross-platform terminal compatibility
  - Async-first architecture

**Alternatives Rejected:**
- `curses`: Low-level, not Windows-native, complex
- `blessed`: Less modern, no CSS-like styling
- `rich` (alone): Textual supersedes it for TUI
- `prompt_toolkit`: More for prompts, less for full apps
- `pytermgui`: Less mature ecosystem

**Nano-task 2.1.1.1.1:** Install textual and verify version  
**Nano-task 2.1.1.1.2:** Create minimal Textual app as proof of concept  
**Nano-task 2.1.1.1.3:** Test on target platforms (Termux, Windows, Linux)

#### Micro-task 2.1.1.2: Base Application Structure

**Nano-task 2.1.1.2.1:** Create `src/tui/app.py`:
```python
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

from src.config.settings import Settings
from src.core.services.user_service import UserService
from src.tui.screens.login_screen import LoginScreen
from src.tui.screens.main_menu_screen import MainMenuScreen

class HikikimoApp(App):
    """Main TUI application container."""
    
    CSS_PATH = "themes/default.tcss"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f1", "help", "Help", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
    ]
    
    # Reactive state - automatically triggers UI updates
    current_user = reactive(None)
    current_screen_id = reactive("login")
    
    def __init__(self, settings: Settings, user_service: UserService):
        super().__init__()
        self.settings = settings
        self.user_service = user_service
        self._setup_encoding()
    
    def _setup_encoding(self):
        """Configure encoding based on terminal capabilities."""
        from src.config.platform import PlatformDetector
        self.platform = PlatformDetector.detect()
        self.capabilities = PlatformDetector.get_terminal_capabilities()
    
    def on_mount(self) -> None:
        """Initialize application on mount."""
        self.push_screen(LoginScreen(self.user_service))
    
    def action_save(self) -> None:
        """Manual save trigger."""
        # Trigger auto-save immediately
        self.notify("Game saved!", severity="information")
    
    def watch_current_user(self, user) -> None:
        """React to user login/logout."""
        if user:
            self.push_screen(MainMenuScreen(user, self.user_service))
        else:
            self.push_screen(LoginScreen(self.user_service))
```

**Nano-task 2.1.1.2.2:** Create `src/tui/themes/default.tcss` with base styling  
**Nano-task 2.1.1.2.3:** Implement theme switching system  
**Nano-task 2.1.1.2.4:** Create dark/light theme variants

### Sub-task 2.1.2: Custom Styling System

#### Micro-task 2.1.2.1: Theme Architecture

**Nano-task 2.1.2.1.1:** Define CSS structure in `src/tui/themes/default.tcss`:
```css
/* Base theme variables */
:root {
    --primary: #6b8e23;
    --primary-dark: #556b2f;
    --accent: #ffd700;
    --background: #1a1a1a;
    --surface: #2d2d2d;
    --text: #e0e0e0;
    --text-muted: #888888;
    --success: #32cd32;
    --warning: #ffa500;
    --error: #ff4444;
    --border: #444444;
}

/* Main layout */
Screen {
    align: center middle;
    background: var(--background);
}

Header {
    background: var(--surface);
    color: var(--text);
    height: 3;
}

Footer {
    background: var(--surface);
    color: var(--text-muted);
    height: 1;
}

/* Game-specific widgets */
StatDisplay {
    background: var(--surface);
    border: solid var(--border);
    padding: 1;
}

StatDisplay .currency {
    color: var(--accent);
}

StatDisplay .xp {
    color: var(--success);
}

StatDisplay .level {
    color: var(--warning);
}

MenuPanel {
    background: var(--surface);
    border: solid var(--border);
    width: 30;
}

MenuPanel:focus {
    border: solid var(--primary);
}

ContentArea {
    background: var(--background);
    border: solid var(--border);
}

/* Buttons */
Button {
    background: var(--primary);
    color: var(--text);
}

Button:hover {
    background: var(--primary-dark);
}

Button.primary {
    background: var(--accent);
    color: var(--background);
}

/* Notifications */
Toast {
    background: var(--surface);
    border: solid var(--primary);
}

Toast.success {
    border: solid var(--success);
}

Toast.error {
    border: solid var(--error);
}
```

**Nano-task 2.1.2.1.2:** Create platform-specific theme variants (limited color support)  
**Nano-task 2.1.2.1.3:** Implement theme hot-reloading for development

---

## Task 2.2: Screen Architecture

### Sub-task 2.2.1: Login & Authentication Screens

#### Micro-task 2.2.1.1: Login Screen Layout

**Nano-task 2.2.1.1.1:** Create `src/tui/screens/login_screen.py`:
```python
from textual.screen import Screen
from textual.widgets import Static, Input, Button, Label, RadioSet, RadioButton
from textual.containers import Vertical, Horizontal, Center
from textual.reactive import reactive

class LoginScreen(Screen):
    """Initial login/create account/guest selection screen."""
    
    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
    }
    
    #login-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    
    #mode-selector {
        margin: 1 0;
    }
    
    .hidden {
        display: none;
    }
    """
    
    current_mode = reactive("login")  # 'login', 'create', 'guest'
    
    def __init__(self, user_service):
        super().__init__()
        self.user_service = user_service
    
    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Static("♨️  Hikikimo Life", id="title")
            yield Static("A peaceful life simulation", classes="subtitle")
            
            with RadioSet(id="mode-selector"):
                yield RadioButton("Login", value=True, id="mode-login")
                yield RadioButton("Create Account", id="mode-create")
                yield RadioButton("Play as Guest", id="mode-guest")
            
            # Login form
            with Vertical(id="login-form"):
                yield Label("Username:")
                yield Input(placeholder="Enter username", id="username")
                yield Label("Password:")
                yield Input(password=True, placeholder="Enter password", id="password")
            
            # Create account form (initially hidden)
            with Vertical(id="create-form", classes="hidden"):
                yield Label("Nickname:")
                yield Input(placeholder="Display name", id="nickname")
                yield Label("Username:")
                yield Input(placeholder="Unique username", id="new-username")
                yield Label("Password:")
                yield Input(password=True, placeholder="Min 4 characters", id="new-password")
                yield Label("Confirm Password:")
                yield Input(password=True, placeholder="Re-enter password", id="confirm-password")
            
            with Horizontal(id="button-row"):
                yield Button("Enter Game", variant="primary", id="enter-btn")
                yield Button("Exit", id="exit-btn")
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Toggle between login/create/guest modes."""
        self.current_mode = event.pressed.id.replace("mode-", "")
        self._update_form_visibility()
    
    def _update_form_visibility(self):
        login_form = self.query_one("#login-form", Vertical)
        create_form = self.query_one("#create-form", Vertical)
        
        if self.current_mode == "login":
            login_form.remove_class("hidden")
            create_form.add_class("hidden")
        elif self.current_mode == "create":
            login_form.add_class("hidden")
            create_form.remove_class("hidden")
        else:  # guest
            login_form.add_class("hidden")
            create_form.add_class("hidden")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "enter-btn":
            self._handle_enter()
        elif event.button.id == "exit-btn":
            self.app.exit()
    
    def _handle_enter(self):
        """Process login/create/guest action."""
        try:
            if self.current_mode == "guest":
                user = self.user_service.create_guest_user()
                self.app.current_user = user
                self.app.notify(f"Welcome, {user.nickname}!", severity="success")
            elif self.current_mode == "login":
                username = self.query_one("#username", Input).value
                password = self.query_one("#password", Input).value
                user = self.user_service.authenticate(username, password)
                self.app.current_user = user
                self.app.notify(f"Welcome back, {user.nickname}!", severity="success")
            else:  # create
                self._handle_create_account()
        except AuthenticationError as e:
            self.notify(str(e), severity="error")
        except ValidationError as e:
            self.notify(str(e), severity="warning")
```

**Nano-task 2.2.1.1.2:** Implement password input masking with confirmation  
**Nano-task 2.2.1.1.3:** Add input validation with real-time feedback  
**Nano-task 2.2.1.1.4:** Implement "hidden" cheat code detection (titit/𓂸) for test mode

#### Micro-task 2.2.1.2: Main Menu Screen Layout

**Nano-task 2.2.1.2.1:** Create `src/tui/screens/main_menu_screen.py` with sidebar navigation:
```python
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Label, DataTable
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

class MainMenuScreen(Screen):
    """Main game screen with sidebar navigation and dynamic content area."""
    
    DEFAULT_CSS = """
    MainMenuScreen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 25;
        dock: left;
        background: $surface;
        border-right: solid $border;
    }
    
    #user-stats {
        height: 6;
        background: $primary-dark;
        padding: 1;
        border-bottom: solid $border;
    }
    
    #main-menu-list {
        height: 1fr;
    }
    
    #content-area {
        width: 1fr;
        background: $background;
    }
    
    ListView:focus {
        background: $primary-dark;
    }
    
    ListItem {
        padding: 1;
    }
    
    ListItem:focus {
        background: $primary;
    }
    """
    
    current_section = reactive("job_center")
    
    def __init__(self, user, user_service):
        super().__init__()
        self.user = user
        self.user_service = user_service
    
    def compose(self) -> ComposeResult:
        # Sidebar with stats and navigation
        with Vertical(id="sidebar"):
            with Static(id="user-stats"):
                yield Label(f"👤 {self.user.nickname}")
                yield Label(f"🪙 {self.user.balance}", classes="currency")
                yield Label(f"⭐ {self.user.xp} XP", classes="xp")
                yield Label(f"🔼 Level {self.user.level}", classes="level")
            
            menu_items = [
                ("job_center", "💼 Job Center"),
                ("casino", "🎰 Casino"),
                ("yard", "🌾 Yard"),
                ("fishing", "🎣 Fishing"),
                ("my_room", "🏠 My Room"),
                ("shop", "🛒 Shop"),
                ("daily", "📅 Daily Rewards"),
                ("leaderboard", "🏆 Leaderboard"),
            ]
            
            with ListView(id="main-menu-list"):
                for section_id, label in menu_items:
                    yield ListItem(Label(label), id=f"menu-{section_id}")
                yield ListItem(Label("🚪 Logout"), id="menu-logout")
        
        # Dynamic content area
        with Vertical(id="content-area"):
            yield Static("Select a menu item from the sidebar", id="content-placeholder")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle menu selection."""
        item_id = event.item.id
        
        if item_id == "menu-logout":
            self.app.current_user = None
            return
        
        section = item_id.replace("menu-", "")
        self.current_section = section
        self._load_section(section)
    
    def _load_section(self, section: str):
        """Load the appropriate section widget."""
        content_area = self.query_one("#content-area", Vertical)
        content_area.remove_children()
        
        if section == "job_center":
            content_area.mount(JobCenterWidget(self.user, self.user_service))
        elif section == "casino":
            content_area.mount(CasinoWidget(self.user, self.user_service))
        elif section == "yard":
            content_area.mount(YardWidget(self.user, self.user_service))
        # ... etc for all sections
    
    def watch_user(self, user):
        """Update stats display when user data changes."""
        stats = self.query_one("#user-stats", Static)
        stats.update(f"👤 {user.nickname}\n🪙 {user.balance}\n⭐ {user.xp} XP\n🔼 Level {user.level}")
```

### Sub-task 2.2.2: Game Section Screens

#### Micro-task 2.2.2.1: Job Center Widget

**Nano-task 2.2.2.1.1:** Create `src/tui/widgets/job_center_widget.py`:
```python
from textual.widgets import Static, Button, Grid, Label, ProgressBar
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

class JobCenterWidget(Static):
    """Job Center section with Work, Trade, and Crime options."""
    
    DEFAULT_CSS = """
    JobCenterWidget {
        padding: 1;
    }
    
    #job-grid {
        grid-size: 3;
        grid-gutter: 1;
    }
    
    JobCard {
        background: $surface;
        border: solid $border;
        padding: 2;
        height: 12;
    }
    
    JobCard:focus {
        border: solid $primary;
    }
    
    JobCard .title {
        text-style: bold;
        text-align: center;
        color: $accent;
    }
    
    JobCard .description {
        color: $text-muted;
        text-align: center;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("💼 Job Center", classes="section-title")
            yield Static("Choose your path to earn coins and XP")
            
            with Grid(id="job-grid"):
                with Static(classes="job-card"):
                    yield Label("🔨 Work", classes="title")
                    yield Label("Honest labor for steady income", classes="description")
                    yield ProgressBar(total=100, value=0, id="work-progress")
                    yield Button("Start Working", id="btn-work")
                
                with Static(classes="job-card"):
                    yield Label("📊 Trade", classes="title")
                    yield Label("Buy low, sell high", classes="description")
                    yield Button("Open Trading Post", id="btn-trade")
                
                with Static(classes="job-card"):
                    yield Label("🗡️ Crime", classes="title")
                    yield Label("High risk, high reward", classes="description")
                    yield Static("⚠️ Risk of losing coins!", classes="warning")
                    yield Button("Plan Heist", variant="error", id="btn-crime")
```

**Nano-task 2.2.2.1.2:** Implement work progress simulation with animation  
**Nano-task 2.2.2.1.3:** Create trading interface with inventory integration  
**Nano-task 2.2.2.1.4:** Implement crime risk/reward system with visual feedback

#### Micro-task 2.2.2.2: Casino Widgets

**Nano-task 2.2.2.2.1:** Create `CasinoWidget` with sub-section navigation  
**Nano-task 2.2.2.2.2:** Implement `SlotsWidget` with animated reels  
**Nano-task 2.2.2.2.3:** Implement `BlackjackWidget` with card display  
**Nano-task 2.2.2.2.4:** Implement `RouletteWidget` with betting grid

#### Micro-task 2.2.2.3: Yard (Farming & Animals) Widgets

**Nano-task 2.2.2.3.1:** Create `YardWidget` with Field/Barn tabs  
**Nano-task 2.2.2.3.2:** Implement `FieldWidget` with visual plot grid  
**Nano-task 2.2.2.3.3:** Implement crop growth visualization  
**Nano-task 2.2.2.3.4:** Create `BarnWidget` with animal slot display

#### Micro-task 2.2.2.4: Fishing Widget

**Nano-task 2.2.2.4.1:** Create `FishingWidget` with location selection  
**Nano-task 2.2.2.4.2:** Implement equipment selection interface  
**Nano-task 2.2.2.4.3:** Create fishing mini-game with timing mechanic  
**Nano-task 2.2.2.4.4:** Implement catch display with rarity indicators

#### Micro-task 2.2.2.5: Inventory & Profile Widgets

**Nano-task 2.2.2.5.1:** Create `InventoryWidget` with category tabs  
**Nano-task 2.2.2.5.2:** Implement item detail view with actions  
**Nano-task 2.2.2.5.3:** Create `ProfileWidget` with stats and achievements  
**Nano-task 2.2.2.5.4:** Implement XP progress bar visualization

#### Micro-task 2.2.2.6: Shop Widget

**Nano-task 2.2.2.6.1:** Create `ShopWidget` with category navigation  
**Nano-task 2.2.2.6.2:** Implement item grid with prices  
**Nano-task 2.2.2.6.3:** Create purchase confirmation dialog  
**Nano-task 2.2.2.6.4:** Add insufficient funds handling

#### Micro-task 2.2.2.7: Daily Rewards Widget

**Nano-task 2.2.2.7.1:** Create `DailyRewardsWidget` with calendar view  
**Nano-task 2.2.2.7.2:** Implement streak visualization  
**Nano-task 2.2.2.7.3:** Add claim reward animation  
**Nano-task 2.2.2.7.4:** Implement next reward preview

#### Micro-task 2.2.2.8: Leaderboard Widget

**Nano-task 2.2.2.8.1:** Create `LeaderboardWidget` with tab navigation  
**Nano-task 2.2.2.8.2:** Implement XP leaderboard table  
**Nano-task 2.2.2.8.3:** Implement Wealth leaderboard table  
**Nano-task 2.2.2.8.4:** Add user rank highlighting

---

## 🔧 EDGE CASE SIMULATION — Phase 2

### Edge Case 2.1: Terminal Resize Handling

**Scenario:** User resizes terminal while game is running.

| Condition | Behavior | Mitigation |
|-----------|----------|------------|
| Width < 80 cols | Enable compact mode | Sidebar collapses to icons only |
| Height < 24 rows | Hide footer, compress headers | Scrollable content areas |
| Resize during input | Preserve input state | Textual handles this natively |
| Mobile rotation (Termux) | Full re-layout | Detect orientation, adapt layout |

**Implementation:**
```python
from textual.reactive import reactive

class ResponsiveLayout(Static):
    compact_mode = reactive(False)
    
    def watch_compact_mode(self, compact: bool):
        sidebar = self.query_one("#sidebar")
        if compact:
            sidebar.styles.width = 3  # Icon only
        else:
            sidebar.styles.width = 25
    
    def on_resize(self, event):
        """Handle terminal resize events."""
        self.compact_mode = event.size.width < 80
```

### Edge Case 2.2: Keyboard Navigation Conflicts

**Scenario:** Different terminals send different key codes.

| Key | Termux | Windows CMD | Windows Terminal | macOS |
|-----|--------|-------------|------------------|-------|
| Arrow keys | \x1b[A-D | Same | Same | Same |
| Enter | \r | \r\n | \r | \r |
| Escape | \x1b | \x1b | \x1b | \x1b |
| Function keys | \x1bOP-F | Different | Same as Termux | Same |
| Ctrl+C | SIGINT | SIGINT | SIGINT | SIGINT |

**Mitigation:** Textual abstracts this, but we add custom bindings for critical actions.

### Edge Case 2.3: TUI Layout Corruption

**Scenario:** Terminal doesn't support certain Unicode or control sequences.

**Detection:**
```python
def validate_terminal(self):
    """Check terminal capabilities on startup."""
    issues = []
    
    if not self.capabilities.supports_unicode:
        issues.append("Unicode not supported - using ASCII fallback")
    
    if self.capabilities.max_colors < 16:
        issues.append("Limited color support - theme simplified")
    
    if self.platform == Platform.WINDOWS_CMD:
        issues.append("Windows CMD detected - some features limited")
    
    if issues:
        self.push_screen(WarningScreen(issues))
```

### Edge Case 2.4: Input Buffer Overflow

**Scenario:** User types rapidly or pastes large text into input fields.

**Mitigation:**
```python
from textual.validation import ValidationResult, Validator

class LimitedLengthValidator(Validator):
    def __init__(self, max_length: int = 32):
        self.max_length = max_length
    
    def validate(self, value: str) -> ValidationResult:
        if len(value) > self.max_length:
            return self.failure(f"Maximum {self.max_length} characters")
        return self.success()

# In compose:
yield Input(
    placeholder="Username",
    validators=[LimitedLengthValidator(32)],
    max_length=32  # Hard limit
)
```

---

# 🗺️ PHASE 3: Business Logic Services & Game Systems

## Task 3.1: Core Service Layer

### Sub-task 3.1.1: User Management Service

#### Micro-task 3.1.1.1: Authentication Service

**Nano-task 3.1.1.1.1:** Create `src/core/services/auth_service.py`:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import bcrypt

from src.core.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions.auth_exceptions import (
    AuthenticationError, UserExistsError, ValidationError
)

@dataclass
class AuthResult:
    user: User
    is_new: bool = False

class AuthService:
    """Handle user authentication with secure password hashing."""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def authenticate(self, username: str, password: str) -> User:
        """Authenticate user with bcrypt password verification."""
        user = self.user_repo.get_by_username(username)
        if not user:
            raise AuthenticationError("Account not found")
        
        if not bcrypt.checkpw(password.encode(), user.password_hash):
            raise AuthenticationError("Invalid password")
        
        # Update last login
        user.last_login = datetime.now()
        self.user_repo.update(user)
        
        return user
    
    def create_account(
        self, 
        nickname: str, 
        username: str, 
        password: str,
        confirm_password: str
    ) -> User:
        """Create new user account with validation."""
        # Validation
        if len(password) < 4:
            raise ValidationError("Password must be at least 4 characters")
        
        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        if self.user_repo.get_by_username(username):
            raise UserExistsError(f"Username '{username}' is taken")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        user = User(
            id=str(uuid.uuid4())[:8],
            username=username,
            nickname=nickname,
            password_hash=password_hash,
            created_at=datetime.now()
        )
        
        return self.user_repo.create(user)
    
    def create_guest(self) -> User:
        """Create temporary guest user."""
        return User(
            id="guest",
            username="guest",
            nickname="Guest",
            password_hash=None,
            is_guest=True
        )
```

**Nano-task 3.1.1.1.2:** Implement password strength validation  
**Nano-task 3.1.1.1.3:** Add rate limiting for login attempts  
**Nano-task 3.1.1.1.4:** Create secure session management

#### Micro-task 3.1.1.2: User Profile Service

**Nano-task 3.1.1.2.1:** Create `ProfileService` for user data operations  
**Nano-task 3.1.1.2.2:** Implement XP/Level progression logic  
**Nano-task 3.1.1.2.3:** Add unlock feature management  
**Nano-task 3.1.1.2.4:** Create statistics tracking

### Sub-task 3.1.2: Economy Service

#### Micro-task 3.1.2.1: Transaction System

**Nano-task 3.1.2.1.1:** Create `EconomyService` with atomic transactions:
```python
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

from src.db.sqlite_manager import SQLiteManager

class TransactionType(Enum):
    EARN = "earn"
    SPEND = "spend"
    TRADE = "trade"

@dataclass
class Transaction:
    user_id: str
    type: TransactionType
    amount: int
    description: str
    timestamp: datetime

class EconomyService:
    """Handle all currency operations with transaction logging."""
    
    def __init__(self, db: SQLiteManager, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo
    
    def add_balance(
        self, 
        user: User, 
        amount: int, 
        reason: str,
        log_activity: bool = True
    ) -> bool:
        """Atomically add balance with transaction logging."""
        with self.db.transaction() as conn:
            # Update user balance
            new_balance = user.balance + amount
            conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (new_balance, user.id)
            )
            
            # Log transaction
            conn.execute(
                """INSERT INTO transactions 
                   (user_id, type, amount, description, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user.id, TransactionType.EARN.value, amount, reason, datetime.now())
            )
            
            # Update leaderboard
            conn.execute(
                """INSERT INTO leaderboard (user_id, username, balance)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET
                   balance = ?, last_updated = ?""",
                (user.id, user.username, new_balance, new_balance, datetime.now())
            )
            
            user.balance = new_balance
            return True
    
    def deduct_balance(
        self, 
        user: User, 
        amount: int, 
        reason: str
    ) -> Tuple[bool, Optional[str]]:
        """Deduct balance if sufficient funds exist."""
        if user.balance < amount:
            return False, "Insufficient funds"
        
        with self.db.transaction() as conn:
            new_balance = user.balance - amount
            conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (new_balance, user.id)
            )
            
            conn.execute(
                """INSERT INTO transactions 
                   (user_id, type, amount, description, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user.id, TransactionType.SPEND.value, -amount, reason, datetime.now())
            )
            
            user.balance = new_balance
            return True, None
```

**Nano-task 3.1.2.1.2:** Implement transaction history viewing  
**Nano-task 3.1.2.1.3:** Add balance overflow/underflow protection  
**Nano-task 3.1.2.1.4:** Create audit trail for all transactions

#### Micro-task 3.1.2.2: XP & Progression System

**Nano-task 3.1.2.2.1:** Implement `ProgressionService` with configurable curves  
**Nano-task 3.1.2.2.2:** Create XP gain calculation with multipliers  
**Nano-task 3.1.2.2.3:** Implement level-up detection and rewards  
**Nano-task 3.1.2.2.4:** Add unlock notification system

### Sub-task 3.1.3: Inventory Service

#### Micro-task 3.1.3.1: Item Management

**Nano-task 3.1.3.1.1:** Create `InventoryService` with category support  
**Nano-task 3.1.3.1.2:** Implement add/remove/transfer operations  
**Nano-task 3.1.3.1.3:** Create inventory search and filtering  
**Nano-task 3.1.3.1.4:** Add item usage logic (tools, consumables)

#### Micro-task 3.1.3.2: Equipment System

**Nano-task 3.1.3.2.1:** Implement equipped item tracking  
**Nano-task 3.1.3.2.2:** Create equipment bonus calculation  
**Nano-task 3.1.3.2.3:** Add equipment durability (if applicable)  
**Nano-task 3.1.3.2.4:** Implement auto-equip best available

### Sub-task 3.1.4: Game Feature Services

#### Micro-task 3.1.4.1: Job Center Service

**Nano-task 3.1.4.1.1:** Create `JobService` with work/trade/crime actions  
**Nano-task 3.1.4.1.2:** Implement work progress with time mechanics  
**Nano-task 3.1.4.1.3:** Create trading market with fluctuating prices  
**Nano-task 3.1.4.1.4:** Add crime risk/reward calculation

#### Micro-task 3.1.4.2: Casino Service

**Nano-task 3.1.4.2.1:** Create `CasinoService` with game implementations  
**Nano-task 3.1.4.2.2:** Implement slots with weighted randomization  
**Nano-task 3.1.4.2.3:** Create blackjack game logic (dealer AI)  
**Nano-task 3.1.4.2.4:** Implement roulette betting and payouts  
**Nano-task 3.1.4.2.5:** Add betting limits enforcement

#### Micro-task 3.1.4.3: Farming Service

**Nano-task 3.1.4.3.1:** Create `FarmingService` with crop lifecycle  
**Nano-task 3.1.4.3.2:** Implement plant/water/harvest actions  
**Nano-task 3.1.4.3.3:** Create growth time calculation with offline progress  
**Nano-task 3.1.4.3.4:** Add crop withering mechanics  
**Nano-task 3.1.4.3.5:** Implement weather effects (optional)

#### Micro-task 3.1.4.4: Animal Husbandry Service

**Nano-task 3.1.4.4.1:** Create `BarnService` with animal state tracking  
**Nano-task 3.1.4.4.2:** Implement feeding mechanics  
**Nano-task 3.1.4.4.3:** Create product collection scheduling  
**Nano-task 3.1.4.4.4:** Add animal happiness/health system

#### Micro-task 3.1.4.5: Fishing Service

**Nano-task 3.1.4.5.1:** Create `FishingService` with catch mechanics  
**Nano-task 3.1.4.5.2:** Implement habitat-specific fish tables  
**Nano-task 3.1.4.5.3:** Create equipment bonus calculation  
**Nano-task 3.1.4.5.4:** Add fishing mini-game difficulty scaling

#### Micro-task 3.1.4.6: Shop Service

**Nano-task 3.1.4.6.1:** Create `ShopService` with dynamic pricing  
**Nano-task 3.1.4.6.2:** Implement buy/sell transactions  
**Nano-task 3.1.4.6.3:** Create unlock-gated item filtering  
**Nano-task 3.1.4.6.4:** Add shop restock mechanics (optional)

#### Micro-task 3.1.4.7: Daily Rewards Service

**Nano-task 3.1.4.7.1:** Create `DailyRewardService` with streak tracking  
**Nano-task 3.1.4.7.2:** Implement login detection across days  
**Nano-task 3.1.4.7.3:** Create escalating reward calculation  
**Nano-task 3.1.4.7.4:** Add streak break notification

#### Micro-task 3.1.4.8: Leaderboard Service

**Nano-task 3.1.4.8.1:** Create `LeaderboardService` with ranking  
**Nano-task 3.1.4.8.2:** Implement rank calculation (dense ranking)  
**Nano-task 3.1.4.8.3:** Create top-N queries with user position  
**Nano-task 3.1.4.8.4:** Add leaderboard caching for performance

---

## Task 3.2: Game Loop & State Management

### Sub-task 3.2.1: Game State Container

#### Micro-task 3.2.1.1: Reactive State Management

**Nano-task 3.2.1.1.1:** Create `GameState` container with reactive properties:
```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from textual.reactive import reactive

@dataclass
class GameState:
    """Central reactive state container for the game."""
    
    # Current user (reactive - triggers UI updates)
    current_user: reactive[Optional[User]] = reactive(None)
    
    # Current location/screen
    current_location: reactive[str] = reactive("main_menu")
    
    # Active notifications
    notifications: reactive[list] = reactive(field(default_factory=list))
    
    # Global game settings (shared across screens)
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Pending actions (for confirmation dialogs)
    pending_action: reactive[Optional[Dict]] = reactive(None)
    
    # Last save timestamp
    last_saved: reactive[Optional[datetime]] = reactive(None)
    
    def notify(self, message: str, severity: str = "information"):
        """Add a notification to the queue."""
        self.notifications.append({
            "message": message,
            "severity": severity,
            "timestamp": datetime.now()
        })
```

### Sub-task 3.2.2: Auto-Save System

#### Micro-task 3.2.2.1: Background Saving

**Nano-task 3.2.2.1.1:** Implement `AutoSaveManager` with Textual's interval timer:
```python
from textual.message import Message

class AutoSaveManager:
    """Manages automatic game saving."""
    
    def __init__(self, app, interval_seconds: int = 300):
        self.app = app
        self.interval = interval_seconds
        self._save_timer = None
    
    def start(self):
        """Start auto-save timer."""
        self._save_timer = self.app.set_interval(
            self.interval, 
            self._do_save
        )
    
    def stop(self):
        """Stop auto-save timer."""
        if self._save_timer:
            self._save_timer.stop()
    
    def _do_save(self):
        """Perform save operation."""
        if self.app.current_user and not self.app.current_user.is_guest:
            try:
                self.app.user_service.save_user(self.app.current_user)
                self.app.state.last_saved = datetime.now()
                self.app.log("Auto-save completed")
            except Exception as e:
                self.app.log(f"Auto-save failed: {e}")
```

**Nano-task 3.2.2.1.2:** Implement save-on-exit  
**Nano-task 3.2.2.1.3:** Add save conflict detection (concurrent modifications)  
**Nano-task 3.2.2.1.4:** Create manual save trigger (Ctrl+S)

---

## 🔧 EDGE CASE SIMULATION — Phase 3

### Edge Case 3.1: Concurrent State Modifications

**Scenario:** User performs action while auto-save is running.

| Condition | Risk | Mitigation |
|-----------|------|------------|
| Save during transaction | Data inconsistency | SQLite transactions prevent this |
| UI update during save | Stale data display | Reactive system ensures sync |
| User logout during save | Partial save | Wait for save completion before logout |
| App crash during save | Corruption | WAL mode + atomic writes prevent this |

### Edge Case 3.2: XP/Level Overflow

**Scenario:** User gains XP beyond maximum level.

**Handling:**
```python
def add_xp(self, user: User, amount: int) -> Tuple[bool, str]:
    max_level = self.config.max_level
    
    if user.level >= max_level:
        # Store excess XP or cap it
        user.xp = min(user.xp + amount, self.get_max_xp())
        return False, "Maximum level reached!"
    
    # Normal level up logic...
```

### Edge Case 3.3: Inventory Item Duplication

**Scenario:** Race condition between inventory operations.

**Mitigation:** SQLite row-level locking + application-level semaphores for critical sections.

### Edge Case 3.4: Negative Balance Exploit

**Scenario:** Rapid concurrent spending attempts.

**Mitigation:** Database-level CHECK constraint + application validation:
```sql
ALTER TABLE users ADD CONSTRAINT balance_non_negative 
    CHECK (balance >= 0);
```

---

# 🗺️ PHASE 4: Platform-Specific Optimizations

## Task 4.1: Termux Primary Optimization

### Sub-task 4.1.1: Android/Termux Specifics

#### Micro-task 4.1.1.1: Storage & Permissions

**Nano-task 4.1.1.1.1:** Detect Termux environment and set appropriate paths  
**Nano-task 4.1.1.1.2:** Handle Android scoped storage restrictions  
**Nano-task 4.1.1.1.3:** Implement SAF (Storage Access Framework) fallback for file picking (if needed)  
**Nano-task 4.1.1.1.4:** Add Termux:API integration for notifications (optional)

#### Micro-task 4.1.1.2: Input Optimizations

**Nano-task 4.1.1.2.1:** Optimize touch target sizes for on-screen keyboards  
**Nano-task 4.1.1.2.2:** Add swipe gesture support (via keyboard sequence detection)  
**Nano-task 4.1.1.2.3:** Implement haptic feedback requests (if Termux:API available)  
**Nano-task 4.1.1.2.4:** Add extra-large mode for small screens

#### Micro-task 4.1.1.3: Performance

**Nano-task 4.1.1.3.1:** Optimize for lower-end Android devices  
**Nano-task 4.1.1.3.2:** Reduce animation complexity on slow terminals  
**Nano-task 4.1.1.3.3:** Implement lazy loading for large lists  
**Nano-task 4.1.1.3.4:** Add battery-aware features (reduce polling when low battery)

## Task 4.2: Windows Compatibility

### Sub-task 4.2.1: Windows Console Support

#### Micro-task 4.2.1.1: Legacy CMD Support

**Nano-task 4.2.1.1.1:** Detect Windows CMD and enable ASCII fallback  
**Nano-task 4.2.1.1.2:** Use 16-color palette instead of truecolor  
**Nano-task 4.2.1.1.3:** Replace Unicode box-drawing with ASCII alternatives  
**Nano-task 4.2.1.1.4:** Test on Windows 7/8/10/11 CMD

#### Micro-task 4.2.1.2: Windows Terminal Support

**Nano-task 4.2.1.2.1:** Enable full features on Windows Terminal  
**Nano-task 4.2.1.2.2:** Use Windows-specific key codes for special keys  
**Nano-task 4.2.1.2.3:** Handle Windows path separators throughout  
**Nano-task 4.2.1.2.4:** Test PowerShell compatibility

#### Micro-task 4.2.1.3: WSL Detection

**Nano-task 4.2.1.3.1:** Detect WSL environment  
**Nano-task 4.2.1.3.2:** Prefer Linux paths over Windows paths in WSL  
**Nano-task 4.2.1.3.3:** Handle interop file access (if needed)

## Task 4.3: Linux/macOS Support

### Sub-task 4.3.1: Unix-like System Support

#### Micro-task 4.3.1.1: XDG Specification Compliance

**Nano-task 4.3.1.1.1:** Use `$XDG_DATA_HOME` if set  
**Nano-task 4.3.1.1.2:** Fallback to `~/.local/share/hkkm` on Linux  
**Nano-task 4.3.1.1.3:** Use `~/Library/Application Support` on macOS  
**Nano-task 4.3.1.1.4:** Create config directory with proper permissions

#### Micro-task 4.3.1.2: Terminal Emulation Support

**Nano-task 4.3.1.2.1:** Test on popular terminals (gnome-terminal, konsole, xterm, alacritty)  
**Nano-task 4.3.1.2.2:** Add terminfo-based capability detection  
**Nano-task 4.3.1.2.3:** Handle missing or incomplete terminfo databases

---

## 🔧 EDGE CASE SIMULATION — Phase 4

### Edge Case 4.1: Termux Session Termination

**Scenario:** Android kills Termux session due to memory pressure.

**Mitigation:**
- Auto-save every 30 seconds (configurable)
- Save on every significant action (purchase, level up)
- Restore state on next launch (if save exists)
- Show "recovery" dialog on restart

### Edge Case 4.2: Windows Defender/Antivirus False Positives

**Scenario:** Executable/script flagged by antivirus.

**Mitigation:**
- No compiled executables (pure Python)
- Clear documentation about false positives
- Sign releases if creating binaries (PyInstaller)

### Edge Case 4.3: macOS Gatekeeper

**Scenario:** macOS quarantines downloaded script.

**Mitigation:**
- Provide installation via pip (trusted source)
- Document `xattr -d com.apple.quarantine` if needed
- Consider code signing for distribution

---

# 🗺️ PHASE 5: Testing, Quality Assurance & Deployment

## Task 5.1: Testing Strategy

### Sub-task 5.1.1: Unit Testing

#### Micro-task 5.1.1.1: Service Layer Tests

**Nano-task 5.1.1.1.1:** Create pytest fixtures for in-memory SQLite  
**Nano-task 5.1.1.1.2:** Test all repository methods with edge cases  
**Nano-task 5.1.1.1.3:** Test service business logic with mocked dependencies  
**Nano-task 5.1.1.1.4:** Achieve >80% coverage on core module

#### Micro-task 5.1.1.2: Model Tests

**Nano-task 5.1.1.2.1:** Test data class validation (Pydantic)  
**Nano-task 5.1.1.2.2:** Test serialization/deserialization  
**Nano-task 5.1.1.2.3:** Test model relationships and constraints

### Sub-task 5.1.2: Integration Testing

#### Micro-task 5.1.2.1: Database Integration

**Nano-task 5.1.2.1.1:** Test migration system (up/down)  
**Nano-task 5.1.2.1.2:** Test concurrent access patterns  
**Nano-task 5.1.2.1.3:** Test database recovery from corruption

#### Micro-task 5.1.2.2: TUI Integration

**Nano-task 5.1.2.2.1:** Test screen navigation flow  
**Nano-task 5.1.2.2.2:** Test reactive state updates  
**Nano-task 5.1.2.2.3:** Test widget interactions using Textual's pilot

### Sub-task 5.1.3: End-to-End Testing

#### Micro-task 5.1.3.1: Terminal Emulation Tests

**Nano-task 5.1.3.1.1:** Create GitHub Actions matrix for all platforms  
**Nano-task 5.1.3.1.2:** Test on Windows (CMD, PowerShell, Windows Terminal)  
**Nano-task 5.1.3.1.3:** Test on Ubuntu, macOS latest  
**Nano-task 5.1.3.1.4:** Create Docker-based Termux simulation (if possible)

#### Micro-task 5.1.3.2: User Journey Tests

**Nano-task 5.1.3.2.1:** Test full account creation → login → gameplay flow  
**Nano-task 5.1.3.2.2:** Test guest mode gameplay  
**Nano-task 5.1.3.2.3:** Test all game features end-to-end  
**Nano-task 5.1.3.2.4:** Test save/load persistence

## Task 5.2: Code Quality

### Sub-task 5.2.1: Static Analysis

#### Micro-task 5.2.1.1: Linting & Formatting

**Nano-task 5.2.1.1.1:** Configure ruff for linting (replaces flake8, pylint)  
**Nano-task 5.2.1.1.2:** Configure black for code formatting  
**Nano-task 5.2.1.1.3:** Set up pre-commit hooks  
**Nano-task 5.2.1.1.4:** Configure mypy for type checking (strict mode)

#### Micro-task 5.2.1.2: Documentation

**Nano-task 5.2.1.2.1:** Add docstrings to all public APIs (Google style)  
**Nano-task 5.2.1.2.2:** Generate API documentation with mkdocs  
**Nano-task 5.2.1.2.3:** Create architecture decision records (ADRs)  
**Nano-task 5.2.1.2.4:** Update README with new installation instructions

### Sub-task 5.2.2: Performance Optimization

#### Micro-task 5.2.2.1: Profiling

**Nano-task 5.2.2.1.1:** Profile database queries with sqlite3 profiler  
**Nano-task 5.2.2.1.2:** Profile TUI rendering with Textual dev tools  
**Nano-task 5.2.2.1.3:** Identify and optimize slow paths  
**Nano-task 5.2.2.1.4:** Add performance regression tests

#### Micro-task 5.2.2.2: Optimization

**Nano-task 5.2.2.2.1:** Add database query caching where appropriate  
**Nano-task 5.2.2.2.2:** Optimize widget re-rendering  
**Nano-task 5.2.2.2.3:** Implement virtual scrolling for long lists  
**Nano-task 5.2.2.2.4:** Add lazy loading for non-critical data

## Task 5.3: Deployment & Distribution

### Sub-task 5.3.1: Package Distribution

#### Micro-task 5.3.1.1: PyPI Package

**Nano-task 5.3.1.1.1:** Prepare `pyproject.toml` for distribution  
**Nano-task 5.3.1.1.2:** Create source distribution (sdist)  
**Nano-task 5.3.1.1.3:** Create wheel distribution  
**Nano-task 5.3.1.1.4:** Upload to PyPI test server first  
**Nano-task 5.3.1.1.5:** Release to PyPI production

#### Micro-task 5.3.1.2: Termux Package

**Nano-task 5.3.1.2.1:** Create Termux build script  
**Nano-task 5.3.1.2.2:** Document Termux-specific installation  
**Nano-task 5.3.1.2.3:** Create `pkg install` instructions (if submitting to Termux repos)

### Sub-task 5.3.2: Documentation

#### Micro-task 5.3.2.1: User Documentation

**Nano-task 5.3.2.1.1:** Rewrite INSTALL.md with TUI focus  
**Nano-task 5.3.2.1.2:** Create USAGE.md with keyboard shortcuts reference  
**Nano-task 5.3.2.1.3:** Add troubleshooting guide for common issues  
**Nano-task 5.3.2.1.4:** Create video/GIF demo of TUI features

#### Micro-task 5.3.2.2: Developer Documentation

**Nano-task 5.3.2.2.1:** Document architecture overview  
**Nano-task 5.3.2.2.2:** Create contribution guidelines  
**Nano-task 5.3.2.2.3:** Document testing procedures  
**Nano-task 5.3.2.2.4:** Add code style guide

---

# 🗺️ PHASE 6: Advanced Features & Polish

## Task 6.1: Accessibility

### Sub-task 6.1.1: Screen Reader Support

#### Micro-task 6.1.1.1: ARIA-like Annotations

**Nano-task 6.1.1.1.1:** Add descriptive labels to all interactive elements  
**Nano-task 6.1.1.1.2:** Implement focus announcements  
**Nano-task 6.1.1.1.3:** Test with common terminal screen readers (orca, NVDA)  
**Nano-task 6.1.1.1.4:** Provide high-contrast theme option

### Sub-task 6.1.2: Input Alternatives

#### Micro-task 6.1.2.1: Vi/Vim Mode

**Nano-task 6.1.2.1.1:** Implement hjkl navigation option  
**Nano-task 6.1.2.1.2:** Add modal editing for text inputs  
**Nano-task 6.1.2.1.3:** Create vim-like command palette

## Task 6.2: Developer Features

### Sub-task 6.2.1: Debug & Test Mode

#### Micro-task 6.2.1.1: Hidden Test Center (Legacy)

**Nano-task 6.2.1.1.1:** Port existing test module (`titit`/`𓂸` cheat code)  
**Nano-task 6.2.1.1.2:** Add new TUI-based test controls  
**Nano-task 6.2.1.1.3:** Implement safe mode for test operations  
**Nano-task 6.2.1.1.4:** Add feature flags for enabling test mode

### Sub-task 6.2.2: Analytics (Optional)

#### Micro-task 6.2.2.1: Usage Analytics

**Nano-task 6.2.2.1.1:** Add opt-in analytics  
**Nano-task 6.2.2.1.2:** Track feature usage (privacy-preserving)  
**Nano-task 6.2.2.1.3:** Add crash reporting (opt-in)

---

# 📊 Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 2 weeks | SQLite schema, repositories, migration scripts |
| **Phase 2** | 3 weeks | Textual TUI setup, all screens, responsive layout |
| **Phase 3** | 3 weeks | All service implementations, game logic |
| **Phase 4** | 1 week | Platform testing, optimizations |
| **Phase 5** | 2 weeks | Testing, CI/CD, documentation |
| **Phase 6** | 1 week | Polish, accessibility, advanced features |

**Total Estimated Duration: 12 weeks**

---

# 🎯 Success Criteria

1. **Functional:** All original CLI features work in TUI
2. **Performance:** <100ms response time for UI interactions
3. **Compatibility:** Runs on Termux, Windows (CMD/PS), Linux, macOS
4. **Reliability:** Zero data loss, auto-save every 30s
5. **Maintainability:** >80% test coverage, clean architecture
6. **User Experience:** Intuitive keyboard navigation, visual feedback

---

# 📝 Appendix: Data Models

## User Model
```python
@dataclass
class User:
    id: str
    username: str
    nickname: str
    password_hash: Optional[bytes]  # bcrypt hash
    xp: int = 0
    level: int = 1
    balance: int = 500
    inventory: Inventory = field(default_factory=dict)
    unlocked_features: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_guest: bool = False
```

## Inventory Model
```python
@dataclass
class InventoryItem:
    item_type: str  # 'tools', 'rods', 'baits', 'seeds', 'feeds', 'fish', 'crops', 'products'
    item_id: int
    quantity: int
    acquired_at: datetime

@dataclass
class Inventory:
    items: Dict[str, List[InventoryItem]] = field(default_factory=dict)
    equipped_rod: Optional[int] = None
    equipped_tool: Optional[int] = None
```

---

*End of Modernization Roadmap*
