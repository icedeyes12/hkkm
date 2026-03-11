#!/usr/bin/env python3
"""CLI entry point for Hikikimo Life."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.db.sqlite_manager import SQLiteManager, init_database
from src.config.settings import get_settings


def setup_database():
    """Initialize database and seed data."""
    print("🔧 Setting up database...")
    settings = get_settings()

    # Ensure data directory exists
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_database()
    print("✅ Database ready!")


def run_tui():
    """Launch the TUI application."""
    from src.tui.app import run_app
    run_app()


def migrate_legacy():
    """Migrate legacy JSON data to SQLite."""
    print("🔄 Running migration...")
    try:
        from scripts.migrate_data import DataMigrator
        migrator = DataMigrator(get_settings())
        results = migrator.migrate_all()
        print(f"✅ Migration complete: {results['users']} users, {results['inventory']} inventory items")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="hkkm",
        description="Hikikimo Life - Terminal Life Simulation Game",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup database and exit",
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate legacy JSON data",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    if args.setup:
        setup_database()
        return

    if args.migrate:
        migrate_legacy()
        return

    # Setup and run
    setup_database()
    run_tui()


if __name__ == "__main__":
    main()
