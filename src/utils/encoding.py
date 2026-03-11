"""Unicode and encoding utilities."""

from __future__ import annotations

import sys
from typing import Optional

from src.config.platform import Platform, PlatformDetector, detected_capabilities


def get_preferred_encoding() -> str:
    """Get the preferred encoding for the current terminal."""
    return detected_capabilities.preferred_encoding


def supports_unicode() -> bool:
    """Check if terminal supports Unicode characters."""
    return detected_capabilities.supports_unicode


def safe_print(text: str, fallback: str = "?") -> None:
    """Print text safely, handling encoding issues.

    Args:
        text: Text to print
        fallback: Replacement for unencodable characters
    """
    if supports_unicode():
        print(text)
        return

    # Try to encode, replace problematic characters
    try:
        encoded = text.encode(get_preferred_encoding(), errors="replace")
        print(encoded.decode(get_preferred_encoding()))
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Last resort: ASCII only
        safe_text = text.encode("ascii", errors="replace").decode("ascii")
        print(safe_text)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Args:
        text: Original text
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def pad_text(text: str, width: int, align: str = "left") -> str:
    """Pad text to specified width.

    Args:
        text: Original text
        width: Target width
        align: Alignment ('left', 'right', 'center')

    Returns:
        Padded text
    """
    if align == "left":
        return text.ljust(width)
    if align == "right":
        return text.rjust(width)
    if align == "center":
        return text.center(width)
    return text


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text.

    Args:
        text: Text possibly containing ANSI codes

    Returns:
        Clean text without ANSI codes
    """
    import re

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def visual_length(text: str) -> int:
    """Get visual length of text (excluding ANSI codes).

    Args:
        text: Text to measure

    Returns:
        Visual character count
    """
    return len(strip_ansi(text))


def get_ascii_art(name: str) -> Optional[str]:
    """Load ASCII art by name.

    Args:
        name: Name of the ASCII art file (without .txt)

    Returns:
        ASCII art string or None if not found
    """
    from pathlib import Path

    art_path = Path(__file__).parent.parent.parent / "assets" / "ascii_art" / f"{name}.txt"
    if not art_path.exists():
        return None

    try:
        with open(art_path, "r", encoding="utf-8") as f:
            return f.read()
    except (IOError, UnicodeDecodeError):
        return None
