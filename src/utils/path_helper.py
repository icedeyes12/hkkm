"""Cross-platform path handling utilities."""

from __future__ import annotations

import os
from pathlib import Path

from src.config.platform import Platform, PlatformDetector


def get_save_path(filename: str) -> Path:
    """Get platform-appropriate save file path.

    Args:
        filename: Name of the save file

    Returns:
        Full path to save location
    """
    data_dir = _get_data_directory()
    saves_dir = data_dir / "saves"
    saves_dir.mkdir(parents=True, exist_ok=True)
    return saves_dir / filename


def get_config_path() -> Path:
    """Get path for configuration files."""
    data_dir = _get_data_directory()
    return data_dir


def get_data_directory() -> Path:
    """Get main data directory for the application."""
    return _get_data_directory()


def _get_data_directory() -> Path:
    """Internal: get data directory based on platform."""
    platform = PlatformDetector.detect()

    if platform == Platform.TERMUX:
        # Termux: use home directory
        return Path(os.environ.get("HOME", "/data/data/com.termux/files/home")) / ".hkkm"

    if platform == Platform.MACOS:
        # macOS: use Application Support
        return Path.home() / "Library" / "Application Support" / "HikikimoLife"

    # Linux, WSL, Windows: use platformdirs if available
    try:
        from platformdirs import user_data_dir
        return Path(user_data_dir("hkkm", appauthor=False))
    except ImportError:
        # Fallback to ~/.local/share/hkkm
        return Path.home() / ".local" / "share" / "hkkm"


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        The path (unchanged)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    """Convert string to safe filename.

    Args:
        name: Original name

    Returns:
        Safe filename string
    """
    # Remove or replace unsafe characters
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        name = name.replace(char, '_')
    return name.strip('. ')


def get_backup_path(original: Path, suffix: str = "bak") -> Path:
    """Generate backup path for a file.

    Args:
        original: Original file path
        suffix: Backup suffix

    Returns:
        Backup file path
    """
    return original.with_suffix(f"{original.suffix}.{suffix}")


def is_writable(path: Path) -> bool:
    """Check if path is writable.

    Args:
        path: Path to check

    Returns:
        True if writable, False otherwise
    """
    try:
        if path.exists():
            return os.access(path, os.W_OK)
        # Check parent directory
        return os.access(path.parent, os.W_OK)
    except OSError:
        return False
