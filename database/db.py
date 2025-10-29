"""
SQLite database operations for fleet manager
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """Handle all database operations"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Miners table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS miners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT UNIQUE NOT NULL,
                    miner_type TEXT NOT NULL,
                    model TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    miner_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hashrate REAL,
                    temperature REAL,
                    power REAL,
                    fan_speed INTEGER,
                    status TEXT,
                    FOREIGN KEY (miner_id) REFERENCES miners(id)
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stats_miner_id
                ON stats(miner_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stats_timestamp
                ON stats(timestamp)
            """)

            logger.info("Database initialized successfully")

    def add_miner(self, ip: str, miner_type: str, model: str = None) -> int:
        """Add a new miner to the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO miners (ip, miner_type, model, discovered_at, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, (ip, miner_type, model, datetime.now(), datetime.now()))
            return cursor.lastrowid

    def update_miner(self, ip: str, miner_type: str, model: str = None):
        """Update existing miner or add if not exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO miners (ip, miner_type, model, discovered_at, last_seen)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(ip) DO UPDATE SET
                    miner_type = excluded.miner_type,
                    model = excluded.model,
                    last_seen = excluded.last_seen
            """, (ip, miner_type, model, datetime.now(), datetime.now()))

    def get_all_miners(self) -> List[Dict]:
        """Get all miners from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM miners ORDER BY ip")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_miner_by_ip(self, ip: str) -> Optional[Dict]:
        """Get specific miner by IP"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM miners WHERE ip = ?", (ip,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_stats(self, miner_id: int, hashrate: float = None,
                  temperature: float = None, power: float = None,
                  fan_speed: int = None, status: str = "online"):
        """Add stats entry for a miner"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stats (miner_id, hashrate, temperature, power, fan_speed, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (miner_id, hashrate, temperature, power, fan_speed, status))

    def get_latest_stats(self, miner_id: int) -> Optional[Dict]:
        """Get latest stats for a miner"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stats
                WHERE miner_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (miner_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_historical_stats(self, miner_id: int, limit: int = 100) -> List[Dict]:
        """Get historical stats for a miner"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stats
                WHERE miner_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (miner_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_miner(self, ip: str):
        """Delete a miner and its stats"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Get miner_id first
            cursor.execute("SELECT id FROM miners WHERE ip = ?", (ip,))
            row = cursor.fetchone()
            if row:
                miner_id = row['id']
                # Delete stats
                cursor.execute("DELETE FROM stats WHERE miner_id = ?", (miner_id,))
                # Delete miner
                cursor.execute("DELETE FROM miners WHERE id = ?", (miner_id,))
                logger.info(f"Deleted miner {ip}")
