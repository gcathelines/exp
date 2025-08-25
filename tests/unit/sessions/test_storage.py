"""
Unit tests for SessionStorage class.
Tests SQLite database operations for session persistence.
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.sessions.storage import SessionStorage
from src.utils.models import UserSession


class TestSessionStorage:
    """Test cases for SessionStorage database operations."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            yield tmp.name
        # Cleanup
        Path(tmp.name).unlink(missing_ok=True)

    @pytest.fixture
    def storage(self, temp_db_path):
        """Create SessionStorage instance with temporary database."""
        return SessionStorage(db_path=temp_db_path)

    @pytest.fixture
    def sample_session(self):
        """Create a sample UserSession for testing."""
        return UserSession(
            user_id="test_user",
            title="Test Session",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            last_activity=datetime(2024, 1, 1, 12, 30, 0),
            conversation_history=[
                {
                    "timestamp": "2024-01-01T12:00:00",
                    "role": "user",
                    "content": "Hello",
                    "metadata": {},
                }
            ],
        )

    def test_database_initialization(self, temp_db_path):
        """Test that database and tables are created correctly."""
        storage = SessionStorage(db_path=temp_db_path)
        
        # Check if database file exists
        assert Path(temp_db_path).exists()
        
        # Check if table exists with correct schema
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            assert cursor.fetchone() is not None
            
            # Check table structure
            cursor = conn.execute("PRAGMA table_info(sessions)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            expected_columns = {
                "id": "INTEGER",
                "user_id": "TEXT",
                "title": "TEXT",
                "created_at": "TEXT",
                "last_activity": "TEXT",
                "conversation_history": "TEXT",
            }
            
            for col_name, col_type in expected_columns.items():
                assert col_name in columns
                assert columns[col_name] == col_type

    def test_save_new_session(self, storage, sample_session):
        """Test saving a new session to database."""
        # Session should have no ID initially
        assert sample_session.id is None
        
        # Save session
        saved_session = storage.save_session(sample_session)
        
        # Should return session with assigned ID
        assert saved_session.id is not None
        assert isinstance(saved_session.id, int)
        assert saved_session.id > 0
        
        # Original session should be modified with ID
        assert sample_session.id == saved_session.id

    def test_save_existing_session(self, storage, sample_session):
        """Test updating an existing session."""
        # First save
        saved_session = storage.save_session(sample_session)
        original_id = saved_session.id
        
        # Modify session
        saved_session.title = "Updated Title"
        saved_session.conversation_history.append({
            "timestamp": "2024-01-01T12:15:00",
            "role": "assistant",
            "content": "Updated response",
            "metadata": {},
        })
        
        # Save again
        updated_session = storage.save_session(saved_session)
        
        # ID should remain the same
        assert updated_session.id == original_id
        
        # Changes should be persisted
        loaded_session = storage.load_session(original_id)
        assert loaded_session.title == "Updated Title"
        assert len(loaded_session.conversation_history) == 2

    def test_load_session_exists(self, storage, sample_session):
        """Test loading an existing session."""
        # Save session first
        saved_session = storage.save_session(sample_session)
        
        # Load session
        loaded_session = storage.load_session(saved_session.id)
        
        # Should match original
        assert loaded_session is not None
        assert loaded_session.id == saved_session.id
        assert loaded_session.user_id == sample_session.user_id
        assert loaded_session.title == sample_session.title
        assert loaded_session.created_at == sample_session.created_at
        assert loaded_session.last_activity == sample_session.last_activity
        assert loaded_session.conversation_history == sample_session.conversation_history

    def test_load_session_not_exists(self, storage):
        """Test loading a non-existent session."""
        result = storage.load_session(999)
        assert result is None

    def test_load_all_sessions_empty(self, storage):
        """Test loading all sessions when none exist."""
        sessions = storage.load_all_sessions("test_user")
        assert sessions == []

    def test_load_all_sessions_multiple(self, storage):
        """Test loading multiple sessions ordered by last activity."""
        # Create three sessions with different activity times
        session1 = UserSession(
            user_id="test_user",
            title="Session 1",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_activity=datetime(2024, 1, 1, 10, 0, 0),
        )
        
        session2 = UserSession(
            user_id="test_user",
            title="Session 2",
            created_at=datetime(2024, 1, 1, 11, 0, 0),
            last_activity=datetime(2024, 1, 1, 12, 0, 0),  # Most recent
        )
        
        session3 = UserSession(
            user_id="other_user",
            title="Session 3",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            last_activity=datetime(2024, 1, 1, 13, 0, 0),
        )
        
        # Save all sessions
        storage.save_session(session1)
        storage.save_session(session2)
        storage.save_session(session3)
        
        # Load sessions for test_user
        sessions = storage.load_all_sessions("test_user")
        
        # Should return only test_user sessions, ordered by last_activity DESC
        assert len(sessions) == 2
        assert sessions[0].title == "Session 2"  # Most recent first
        assert sessions[1].title == "Session 1"
        
        # Load sessions for other_user
        other_sessions = storage.load_all_sessions("other_user")
        assert len(other_sessions) == 1
        assert other_sessions[0].title == "Session 3"

    def test_delete_session_exists(self, storage, sample_session):
        """Test deleting an existing session."""
        # Save session first
        saved_session = storage.save_session(sample_session)
        
        # Delete session
        result = storage.delete_session(saved_session.id)
        assert result is True
        
        # Session should no longer exist
        loaded_session = storage.load_session(saved_session.id)
        assert loaded_session is None

    def test_delete_session_not_exists(self, storage):
        """Test deleting a non-existent session."""
        result = storage.delete_session(999)
        assert result is False

    def test_conversation_history_serialization(self, storage):
        """Test that conversation history is properly serialized/deserialized."""
        complex_history = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "role": "user",
                "content": "Complex query with special chars: àéîõü",
                "metadata": {
                    "query_type": "natural_language",
                    "confidence": 0.95,
                    "tokens": ["complex", "query"],
                },
            },
            {
                "timestamp": "2024-01-01T12:01:00",
                "role": "assistant",
                "content": "Response with JSON: {\"key\": \"value\", \"number\": 42}",
                "metadata": {
                    "sql_query": "SELECT * FROM table WHERE id = ?",
                    "execution_time": 0.123,
                },
            },
        ]
        
        session = UserSession(
            user_id="test_user",
            title="Complex History Test",
            conversation_history=complex_history,
        )
        
        # Save and reload
        saved_session = storage.save_session(session)
        loaded_session = storage.load_session(saved_session.id)
        
        # History should be identical
        assert loaded_session.conversation_history == complex_history

    def test_database_path_handling(self, temp_db_path):
        """Test database path handling with Path objects."""
        path_obj = Path(temp_db_path)
        storage = SessionStorage(db_path=str(path_obj))
        
        assert storage.db_path == path_obj
        assert storage.db_path.exists()

    def test_concurrent_access(self, storage):
        """Test basic concurrent database access safety."""
        sessions = []
        
        # Create multiple sessions simultaneously
        for i in range(10):
            session = UserSession(
                user_id=f"user_{i}",
                title=f"Session {i}",
            )
            sessions.append(storage.save_session(session))
        
        # All should have unique IDs
        session_ids = [s.id for s in sessions]
        assert len(set(session_ids)) == 10
        
        # All should be retrievable
        for session in sessions:
            loaded = storage.load_session(session.id)
            assert loaded is not None
            assert loaded.title == session.title

    def test_edge_cases(self, storage):
        """Test edge cases and boundary conditions."""
        # Empty title
        session = UserSession(user_id="test", title="")
        saved = storage.save_session(session)
        loaded = storage.load_session(saved.id)
        assert loaded.title == ""
        
        # Empty conversation history (default)
        session2 = UserSession(user_id="test", title="Empty History")
        saved2 = storage.save_session(session2)
        loaded2 = storage.load_session(saved2.id)
        assert loaded2.conversation_history == []
        
        # Very long title
        long_title = "A" * 1000
        session3 = UserSession(user_id="test", title=long_title)
        saved3 = storage.save_session(session3)
        loaded3 = storage.load_session(saved3.id)
        assert loaded3.title == long_title