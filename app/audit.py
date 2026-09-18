"""
Audit logging for API-Sentinel.

Records every request decision (allowed or blocked) to a local SQLite
database so history can be queried later via the admin endpoint.
"""

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "audit.db"


@dataclass
class AuditEntry:
    timestamp: str
    user_id: str
    endpoint: str
    method: str
    allowed: bool
    reason: str


class AuditLogger:
    """Thread-safe SQLite-backed audit logger."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    allowed INTEGER NOT NULL,
                    reason TEXT
                )
                """
            )

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def append(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        allowed: bool,
        reason: str,
    ) -> AuditEntry:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            allowed=allowed,
            reason=reason,
        )
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_log
                    (timestamp, user_id, endpoint, method, allowed, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.timestamp,
                    entry.user_id,
                    entry.endpoint,
                    entry.method,
                    int(entry.allowed),
                    entry.reason,
                ),
            )
        return entry

    def query(
        self,
        user_id: Optional[str] = None,
        allowed: Optional[bool] = None,
        limit: int = 50,
    ):
        clauses, params = [], []
        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(user_id)
        if allowed is not None:
            clauses.append("allowed = ?")
            params.append(int(allowed))

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT timestamp, user_id, endpoint, method, allowed, reason
            FROM audit_log
            {where}
            ORDER BY id DESC
            LIMIT ?
        """
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [
            AuditEntry(
                timestamp=r[0],
                user_id=r[1],
                endpoint=r[2],
                method=r[3],
                allowed=bool(r[4]),
                reason=r[5],
            )
            for r in rows
        ]


# Module-level singleton, mirroring the pattern used by alert_manager
audit_logger = AuditLogger()