"""Local project storage using SQLite."""
import sqlite3
from pathlib import Path
from typing import Any, Optional

_DB_PATH = Path.home() / ".db_norm_checker" / "projects.db"


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _DB_PATH.exists():
        conn = sqlite3.connect(str(_DB_PATH))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_path TEXT,
                    stu_path TEXT,
                    fingerprint_ref TEXT,
                    fingerprint_stu TEXT,
                    fingerprint_match INTEGER,
                    score_4 TEXT,
                    report_html TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()


def save_session(
    ref_path: str,
    stu_path: str,
    fingerprint_ref: str,
    fingerprint_stu: str,
    fingerprint_match: bool,
    score_4: str,
    report_html: str,
) -> int:
    _ensure_db()
    conn = sqlite3.connect(str(_DB_PATH))
    try:
        cur = conn.execute(
            """INSERT INTO sessions (ref_path, stu_path, fingerprint_ref, fingerprint_stu,
               fingerprint_match, score_4, report_html)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ref_path, stu_path, fingerprint_ref, fingerprint_stu, 1 if fingerprint_match else 0, score_4, report_html),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def list_sessions(limit: int = 50) -> list[dict[str, Any]]:
    _ensure_db()
    conn = sqlite3.connect(str(_DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, ref_path, stu_path, fingerprint_match, score_4, created_at FROM sessions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_session(session_id: int) -> Optional[dict[str, Any]]:
    _ensure_db()
    conn = sqlite3.connect(str(_DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
