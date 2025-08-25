"""
Session manager for handling user sessions and conversation history.
Provides high-level API for session operations.
"""

from datetime import datetime
from typing import Any

from src.sessions.storage import SessionStorage
from src.utils.models import UserSession


class SessionManager:
    """High-level session management interface."""

    def __init__(self, storage: SessionStorage | None = None):
        """Initialize session manager with storage backend."""
        self.storage = storage or SessionStorage()

    def create_session(self, title: str, user_id: str = "default_user") -> UserSession:
        """Create a new session."""
        session = UserSession(
            user_id=user_id,
            title=title,
            created_at=datetime.now(),
            last_activity=datetime.now(),
        )

        return self.storage.save_session(session)

    def get_all_sessions(self, user_id: str = "default_user") -> list[UserSession]:
        """Get all sessions for a user."""
        return self.storage.load_all_sessions(user_id)

    def get_session_by_id(self, session_id: int) -> UserSession | None:
        """Get a session by ID."""
        return self.storage.load_session(session_id)

    def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        return self.storage.delete_session(session_id)

    def add_message_to_session(
        self,
        session: UserSession,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a message to a session and save it."""
        session.add_message(role, content, metadata)
        self.storage.save_session(session)

    def update_session_activity(self, session: UserSession) -> None:
        """Update session's last activity and save it."""
        session.last_activity = datetime.now()
        self.storage.save_session(session)
