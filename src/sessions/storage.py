"""
SQLite storage layer for session management.
Handles persistent storage of user sessions and conversation history.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src.utils.models import UserSession


class SessionStorage:
    """SQLite-based storage for user sessions."""

    def __init__(self, db_path: str = "bi_chat_sessions.db"):
        """Initialize SQLite storage with database path."""
        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    conversation_history TEXT NOT NULL
                )
            """)

            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_sessions
                ON sessions(user_id, last_activity DESC)
            """)

            conn.commit()

    def save_session(self, session: UserSession) -> UserSession:
        """Save or update a session in the database."""
        with sqlite3.connect(self.db_path) as conn:
            if session.id is None:
                # Insert new session
                cursor = conn.execute(
                    """
                    INSERT INTO sessions
                    (user_id, title, created_at, last_activity, conversation_history)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        session.user_id,
                        session.title,
                        session.created_at.isoformat(),
                        session.last_activity.isoformat(),
                        json.dumps(session.conversation_history),
                    ),
                )
                session.id = cursor.lastrowid
            else:
                # Update existing session
                conn.execute(
                    """
                    UPDATE sessions
                    SET title = ?, last_activity = ?, conversation_history = ?
                    WHERE id = ?
                    """,
                    (
                        session.title,
                        session.last_activity.isoformat(),
                        json.dumps(session.conversation_history),
                        session.id,
                    ),
                )
            conn.commit()
            return session

    def load_session(self, session_id: int) -> UserSession | None:
        """Load a session from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return UserSession(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                last_activity=datetime.fromisoformat(row["last_activity"]),
                conversation_history=json.loads(row["conversation_history"]),
            )

    def load_all_sessions(self, user_id: str = "default_user") -> list[UserSession]:
        """Load all sessions for a user, ordered by last activity."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM sessions
                WHERE user_id = ?
                ORDER BY last_activity DESC
            """,
                (user_id,),
            )

            sessions = []
            for row in cursor.fetchall():
                session = UserSession(
                    id=row["id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_activity=datetime.fromisoformat(row["last_activity"]),
                    conversation_history=json.loads(row["conversation_history"]),
                )
                sessions.append(session)

            return sessions

    def delete_session(self, session_id: int) -> bool:
        """Delete a session from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
