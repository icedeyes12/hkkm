"""SQLite connection manager with WAL mode and migration support."""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from src.config.platform import Platform, PlatformDetector
from src.config.settings import get_settings
from src.core.exceptions import DatabaseError, MigrationError


class SQLiteManager:
    """Thread-safe SQLite connection manager with WAL mode support."""

    _instance: Optional[SQLiteManager] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> SQLiteManager:
        """Singleton pattern to ensure single database manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        pool_size: int = 5,
        wal_mode: bool = True,
    ) -> None:
        """Initialize SQLite manager.

        Args:
            db_path: Path to database file (defaults to settings)
            pool_size: Connection pool size
            wal_mode: Enable WAL mode for better concurrency
        """
        if hasattr(self, "_initialized"):
            return

        settings = get_settings()

        self.db_path = Path(db_path) if db_path else settings.database_path
        self._pool_size = pool_size
        self._wal_mode = wal_mode
        self._pool: list[sqlite3.Connection] = []
        self._pool_lock = threading.Lock()
        self._local = threading.local()

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()
        self._initialized = True

    def _initialize_database(self) -> None:
        """Initialize database with WAL mode and schema."""
        conn = self._create_connection()
        try:
            # Enable WAL mode for better concurrency
            if self._wal_mode:
                conn.execute("PRAGMA journal_mode=WAL")

            # Performance optimizations
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB

            # Create schema
            self._create_schema(conn)

            # Initialize migration tracking
            self._init_migration_table(conn)

            conn.commit()
        finally:
            conn.close()

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with proper settings."""
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30.0,
            isolation_level=None,  # Autocommit mode for explicit transactions
        )
        conn.row_factory = sqlite3.Row

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")

        return conn

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema."""
        schema_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            nickname TEXT NOT NULL,
            password_hash BLOB,
            xp INTEGER DEFAULT 0 CHECK (xp >= 0),
            level INTEGER DEFAULT 1 CHECK (level >= 1),
            balance INTEGER DEFAULT 500 CHECK (balance >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_guest BOOLEAN DEFAULT 0,
            unlocked_features TEXT DEFAULT '{}' -- JSON
        );

        -- Inventory table
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT DEFAULT '{}', -- JSON
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, item_type, item_id)
        );

        -- Field plots for farming
        CREATE TABLE IF NOT EXISTS field_plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            plot_number INTEGER NOT NULL,
            crop_id INTEGER,
            planted_at TIMESTAMP,
            last_watered TIMESTAMP,
            growth_stage INTEGER DEFAULT 0,
            health INTEGER DEFAULT 100 CHECK (health >= 0 AND health <= 100),
            crop_growth_time INTEGER DEFAULT 0,
            crop_delay_time INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, plot_number)
        );

        -- Barn slots for animals
        CREATE TABLE IF NOT EXISTS barn_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            slot_number INTEGER NOT NULL,
            animal_id INTEGER,
            acquired_at TIMESTAMP,
            last_fed TIMESTAMP,
            happiness INTEGER DEFAULT 50 CHECK (happiness >= 0 AND happiness <= 100),
            product_ready_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, slot_number)
        );

        -- Static game data: Fish
        CREATE TABLE IF NOT EXISTS fish (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            base_price INTEGER NOT NULL,
            xp_reward INTEGER NOT NULL,
            min_weight REAL NOT NULL,
            max_weight REAL NOT NULL,
            habitat TEXT NOT NULL
        );

        -- Static game data: Crops
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            growth_time INTEGER NOT NULL,
            delay_time INTEGER NOT NULL,
            base_price INTEGER NOT NULL,
            xp_reward INTEGER NOT NULL
        );

        -- Static game data: Seeds
        CREATE TABLE IF NOT EXISTS seeds (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            crop_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (crop_id) REFERENCES crops(id)
        );

        -- Static game data: Animals
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL
        );

        -- Static game data: Animal Products
        CREATE TABLE IF NOT EXISTS animal_products (
            id INTEGER PRIMARY KEY,
            animal_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            base_price INTEGER NOT NULL,
            xp_reward INTEGER NOT NULL,
            is_optional BOOLEAN DEFAULT 0,
            FOREIGN KEY (animal_id) REFERENCES animals(id)
        );

        -- Static game data: Items
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            price INTEGER,
            description TEXT,
            attributes TEXT DEFAULT '{}' -- JSON
        );

        -- Leaderboard
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            xp INTEGER DEFAULT 0,
            balance INTEGER DEFAULT 0,
            rank_xp INTEGER,
            rank_wealth INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- Activity log
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            details TEXT, -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """
        conn.executescript(schema_sql)

        # Create indexes
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory(user_id);
        CREATE INDEX IF NOT EXISTS idx_inventory_type ON inventory(item_type);
        CREATE INDEX IF NOT EXISTS idx_field_plots_user ON field_plots(user_id);
        CREATE INDEX IF NOT EXISTS idx_barn_slots_user ON barn_slots(user_id);
        CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at);
        CREATE INDEX IF NOT EXISTS idx_leaderboard_xp ON leaderboard(xp DESC);
        CREATE INDEX IF NOT EXISTS idx_leaderboard_balance ON leaderboard(balance DESC);
        """
        conn.executescript(indexes_sql)

    def _init_migration_table(self, conn: sqlite3.Connection) -> None:
        """Initialize migration tracking table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                checksum TEXT
            )
        """)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection from the pool."""
        conn: Optional[sqlite3.Connection] = None
        is_new = False

        try:
            # Try to get from thread-local
            if hasattr(self._local, "connection"):
                conn = self._local.connection
            else:
                # Get from pool or create new
                with self._pool_lock:
                    if self._pool:
                        conn = self._pool.pop()
                    else:
                        conn = self._create_connection()
                        is_new = True
                self._local.connection = conn

            yield conn

        except sqlite3.Error as e:
            raise DatabaseError(f"Database error: {e}") from e

        finally:
            # Return to pool or close
            if conn and not hasattr(self._local, "connection"):
                with self._pool_lock:
                    if len(self._pool) < self._pool_size:
                        self._pool.append(conn)
                    else:
                        conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Start a transaction context."""
        with self.connection() as conn:
            conn.execute("BEGIN")
            try:
                yield conn
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] = (),
    ) -> sqlite3.Cursor:
        """Execute a single query."""
        with self.connection() as conn:
            return conn.execute(query, parameters)

    def executemany(
        self,
        query: str,
        parameters: list[tuple[Any, ...] | dict[str, Any]],
    ) -> sqlite3.Cursor:
        """Execute a query multiple times."""
        with self.connection() as conn:
            return conn.executemany(query, parameters)

    def executescript(self, script: str) -> sqlite3.Cursor:
        """Execute a SQL script."""
        with self.connection() as conn:
            return conn.executescript(script)

    def fetchone(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] = (),
    ) -> Optional[sqlite3.Row]:
        """Fetch a single row."""
        cursor = self.execute(query, parameters)
        return cursor.fetchone()

    def fetchall(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] = (),
    ) -> list[sqlite3.Row]:
        """Fetch all rows."""
        cursor = self.execute(query, parameters)
        return cursor.fetchall()

    def get_current_version(self) -> int:
        """Get current database schema version."""
        try:
            row = self.fetchone(
                "SELECT MAX(version) as version FROM _migrations"
            )
            return row["version"] if row and row["version"] else 0
        except sqlite3.Error:
            return 0

    def apply_migration(
        self,
        version: int,
        sql: str,
        description: str = "",
    ) -> None:
        """Apply a migration and track it."""
        import hashlib

        checksum = hashlib.sha256(sql.encode()).hexdigest()[:16]

        with self.transaction() as conn:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO _migrations (version, description, checksum) VALUES (?, ?, ?)",
                (version, description, checksum),
            )

    def close_all(self) -> None:
        """Close all pooled connections."""
        with self._pool_lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()

        # Clear thread-local
        if hasattr(self._local, "connection"):
            self._local.connection.close()
            delattr(self._local, "connection")

    def seed_game_data(self, game_data: dict[str, list[dict[str, Any]]]) -> None:
        """Seed static game data (fish, crops, etc.)."""
        with self.transaction() as conn:
            # Fish
            if "fish" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO fish
                    (id, name, rarity, base_price, xp_reward, min_weight, max_weight, habitat)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (f["id"], f["name"], f["rarity"], f["base_price"],
                         f["xp_reward"], f["min_weight"], f["max_weight"], f["habitat"])
                        for f in game_data["fish"]
                    ],
                )

            # Crops
            if "crops" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO crops
                    (id, name, growth_time, delay_time, base_price, xp_reward)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        (c["id"], c["name"], c["growth_time"], c["delay_time"],
                         c["base_price"], c["xp_reward"])
                        for c in game_data["crops"]
                    ],
                )

            # Seeds
            if "seeds" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO seeds
                    (id, name, crop_id, price) VALUES (?, ?, ?, ?)""",
                    [
                        (s["id"], s["name"], s["crop_id"], s["price"])
                        for s in game_data["seeds"]
                    ],
                )

            # Animals
            if "animals" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO animals
                    (id, name, type) VALUES (?, ?, ?)""",
                    [
                        (a["id"], a["name"], a["type"])
                        for a in game_data["animals"]
                    ],
                )

            # Animal Products
            if "animal_products" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO animal_products
                    (id, animal_id, name, base_price, xp_reward, is_optional)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        (p["id"], p["animal_id"], p["name"], p["base_price"],
                         p["xp_reward"], p.get("is_optional", False))
                        for p in game_data["animal_products"]
                    ],
                )

            # Items
            if "items" in game_data:
                conn.executemany(
                    """INSERT OR REPLACE INTO items
                    (id, type, name, price, description, attributes)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        (i["id"], i["type"], i["name"], i.get("price"),
                         i.get("description", ""), json.dumps(i.get("attributes", {})))
                        for i in game_data["items"]
                    ],
                )


def get_db() -> SQLiteManager:
    """Get the global database manager instance."""
    return SQLiteManager()
