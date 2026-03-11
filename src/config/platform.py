"""Platform detection and terminal capability assessment."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Platform(Enum):
    """Supported platforms for Hikikimo Life."""

    TERMUX = auto()
    WINDOWS_CMD = auto()
    WINDOWS_POWERSHELL = auto()
    WINDOWS_TERMINAL = auto()
    LINUX = auto()
    MACOS = auto()
    WSL = auto()
    UNKNOWN = auto()


@dataclass
class TerminalCapabilities:
    """Detected terminal features for adaptive rendering."""

    supports_unicode: bool = True
    supports_truecolor: bool = True
    supports_256_color: bool = True
    max_colors: int = 256
    has_mouse_support: bool = True
    preferred_encoding: str = "utf-8"
    is_interactive: bool = True


class PlatformDetector:
    """Detect platform and terminal capabilities."""

    @staticmethod
    def detect() -> Platform:
        """Detect the current platform."""
        # Check for Termux first (Android)
        if PlatformDetector._is_termux():
            return Platform.TERMUX

        # Check for WSL
        if PlatformDetector._is_wsl():
            return Platform.WSL

        # Check Windows variants
        if sys.platform == "win32":
            if PlatformDetector._is_windows_terminal():
                return Platform.WINDOWS_TERMINAL
            if PlatformDetector._is_powershell():
                return Platform.WINDOWS_POWERSHELL
            return Platform.WINDOWS_CMD

        # Unix-like systems
        if sys.platform == "darwin":
            return Platform.MACOS

        if sys.platform.startswith("linux"):
            return Platform.LINUX

        return Platform.UNKNOWN

    @staticmethod
    def _is_termux() -> bool:
        """Check if running in Termux environment."""
        termux_prefix = os.environ.get("PREFIX", "")
        return "termux" in termux_prefix.lower() or os.path.isdir("/data/data/com.termux")

    @staticmethod
    def _is_wsl() -> bool:
        """Check if running in Windows Subsystem for Linux."""
        try:
            with open("/proc/version", "r", encoding="utf-8") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info or "wsl" in version_info
        except (FileNotFoundError, PermissionError):
            return False

    @staticmethod
    def _is_windows_terminal() -> bool:
        """Check if running in Windows Terminal."""
        wt_session = os.environ.get("WT_SESSION")
        return wt_session is not None

    @staticmethod
    def _is_powershell() -> bool:
        """Check if running in PowerShell."""
        ps_module_path = os.environ.get("PSModulePath", "")
        return bool(ps_module_path) and "PowerShell" in ps_module_path

    @staticmethod
    def get_terminal_capabilities() -> TerminalCapabilities:
        """Detect terminal capabilities."""
        caps = TerminalCapabilities()

        # Check for color support
        colorterm = os.environ.get("COLORTERM", "").lower()
        term = os.environ.get("TERM", "").lower()

        # Truecolor support
        caps.supports_truecolor = colorterm in ("truecolor", "24bit")

        # 256 color support
        caps.supports_256_color = (
            caps.supports_truecolor
            or "256" in term
            or colorterm in ("truecolor", "24bit")
        )

        # Set max colors
        if caps.supports_truecolor:
            caps.max_colors = 16777216
        elif caps.supports_256_color:
            caps.max_colors = 256
        else:
            caps.max_colors = 16

        # Unicode support detection
        caps.supports_unicode = PlatformDetector._detect_unicode_support()

        # Encoding detection
        caps.preferred_encoding = PlatformDetector._detect_encoding()

        # Interactive detection
        caps.is_interactive = sys.stdin.isatty() and sys.stdout.isatty()

        return caps

    @staticmethod
    def _detect_unicode_support() -> bool:
        """Detect if terminal supports Unicode."""
        # Check environment variables
        lang = os.environ.get("LANG", "")
        if "utf" in lang.lower():
            return True

        # Check Python IO encoding
        if sys.stdout.encoding and "utf" in sys.stdout.encoding.lower():
            return True

        # Default to safe choice on Windows CMD
        if sys.platform == "win32" and not PlatformDetector._is_windows_terminal():
            return False

        return True

    @staticmethod
    def _detect_encoding() -> str:
        """Detect preferred encoding."""
        # Check environment
        for env_var in ["LC_ALL", "LC_CTYPE", "LANG"]:
            value = os.environ.get(env_var, "")
            if value:
                return value

        # Check Python stdout encoding
        if sys.stdout.encoding:
            return sys.stdout.encoding

        return "utf-8"

    @staticmethod
    def get_data_dir(platform: Optional[Platform] = None) -> str:
        """Get platform-appropriate data directory."""
        from platformdirs import user_data_dir

        detected = platform or PlatformDetector.detect()

        if detected == Platform.TERMUX:
            # Termux: use Termux home directory
            prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
            return os.path.join(os.path.dirname(prefix), "home", ".hkkm")

        if detected == Platform.MACOS:
            return user_data_dir("hkkm", "HikikimoLife")

        # Linux, WSL, Windows - use platformdirs
        return user_data_dir("hkkm", appauthor=False)


# Singleton instances for convenience
detected_platform = PlatformDetector.detect()
detected_capabilities = PlatformDetector.get_terminal_capabilities()
