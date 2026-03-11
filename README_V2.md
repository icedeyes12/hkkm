# 🎮 Hikikimo Life v2

A modern terminal-based life simulation game with a rich TUI (Terminal User Interface) and SQLite persistence.

## Features

- 🖥️ **Rich TUI**: Built with Textual for a modern terminal experience
- 🗄️ **SQLite Database**: Robust data persistence with WAL mode
- 🐟 **Fishing System**: Multiple habitats, fish rarities, and rewards
- 🌾 **Farming**: Plant, water, and harvest crops with growth stages
- 🐄 **Livestock**: Raise animals and collect products
- 🎰 **Casino Games**: Slots, dice, and more
- 💼 **Jobs & Trading**: Work, trade, and earn
- 🏆 **Leaderboards**: Compete for XP and wealth rankings
- 📱 **Termux Support**: Designed for Android terminals first
- 💻 **Cross-Platform**: Windows, Linux, macOS, WSL support

## Installation

### From PyPI (when published)

```bash
pip install hkkm
hkkm
```

### From Source

```bash
git clone https://github.com/icedeyes12/hkkm.git
cd hkkm
pip install -e .
python -m src.tui.app
```

### Termux (Android)

```bash
pkg update
pkg install python git
pip install textual pydantic platformdirs bcrypt
python -m src.tui.app
```

## Project Structure

```
hkkm/
├── src/
│   ├── core/              # Business logic
│   │   ├── models/        # Data models (User, Inventory, etc.)
│   │   ├── services/      # Business services (game logic)
│   │   ├── repositories/  # Database access layer
│   │   └── exceptions/    # Custom exceptions
│   ├── tui/               # Terminal UI layer
│   │   ├── app.py         # Main TUI application
│   │   ├── screens/       # Screen components
│   │   └── widgets/       # Reusable UI components
│   ├── db/                # Database layer
│   │   ├── sqlite_manager.py
│   │   └── seed_data/
│   ├── config/            # Configuration
│   │   ├── settings.py    # Pydantic settings
│   │   └── platform.py    # Platform detection
│   └── utils/             # Utilities
│       ├── path_helper.py
│       ├── encoding.py
│       └── validators.py
├── tests/                 # Test suite
├── scripts/               # Migration scripts
└── assets/                # Game assets
```

## Configuration

Settings can be configured via environment variables:

```bash
# Database
HKKM_DB__URL=sqlite:///custom.db
HKKM_DB__ECHO=true

# TUI
HKKM_TUI__THEME=dark
HKKM_TUI__ANIMATION_SPEED=1.5

# Game
HKKM_GAME__STARTING_BALANCE=1000
HKKM_GAME__MAX_LEVEL=20
```

Or create a `.env` file in the project root.

## Migration from v1

If you have existing JSON save files from v1:

```bash
python scripts/migrate_data.py
```

This will convert your users.json and game data to the new SQLite format.

## Development

### Setup

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

```bash
black src tests
ruff check src tests
mypy src
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate between widgets |
| `Enter` | Select/confirm |
| `↑/↓` or `j/k` | Navigate lists |
| `Esc` or `q` | Back/cancel |
| `F1` | Help |

Enable vim mode with `HKKM_TUI__VIM_MODE=true`.

## License

MIT License - See LICENSE file for details.
