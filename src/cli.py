#!/usr/bin/env python3
"""CLI entry point - Single player, no auth."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.db.sqlite_manager import SQLiteManager, init_database
from src.db.seed_data.game_data import get_default_game_data
from src.config.settings import get_settings


def setup_database():
    """Initialize database with seed data."""
    print("🔧 Setting up database...")
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    
    db = init_database()
    
    # Seed game data
    game_data = get_default_game_data()
    db.seed_game_data(game_data)
    print(f"✅ Database ready! {len(game_data.get('fish', []))} fish, {len(game_data.get('crops', []))} crops loaded")


def run_tui():
    """Launch the TUI application."""
    from src.tui.app import run_app
    run_app()


def main():
    """Main entry point."""
    setup_database()
    run_tui()


if __name__ == "__main__":
    main()
