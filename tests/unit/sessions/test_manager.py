"""
Unit tests for SessionManager class.
Tests high-level session management operations and integration with storage.
"""

from datetime import datetime
from unittest.mock import Mock, call

import pytest

from src.sessions.manager import SessionManager
from src.sessions.storage import SessionStorage
from src.utils.models import UserSession


class TestSessionManager:
    """Test cases for SessionManager high-level operations."""

    @pytest.fixture
    def mock_storage(self):
        """Mock SessionStorage for testing."""
        return Mock(spec=SessionStorage)

    @pytest.fixture
    def session_manager(self, mock_storage):
        """SessionManager instance with mocked storage."""
        return SessionManager(storage=mock_storage)

    @pytest.fixture
    def sample_session(self):
        """Sample UserSession for testing."""
        return UserSession(
            id=1,
            user_id="test_user",
            title="Test Session",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            last_activity=datetime(2024, 1, 1, 12, 30, 0),
            conversation_history=[],
        )

    def test_init_with_storage(self, mock_storage):
        """Test SessionManager initialization with provided storage."""
        manager = SessionManager(storage=mock_storage)
        assert manager.storage == mock_storage

    def test_init_without_storage(self):
        """Test SessionManager initialization creates default storage."""
        manager = SessionManager()
        assert isinstance(manager.storage, SessionStorage)

    def test_create_session_basic(self, session_manager, mock_storage):
        """Test creating a basic session."""
        # Mock storage response
        expected_session = UserSession(
            id=1,
            user_id="test_user",
            title="New Session",
        )
        mock_storage.save_session.return_value = expected_session

        # Create session
        result = session_manager.create_session("New Session", "test_user")

        # Verify storage was called correctly
        mock_storage.save_session.assert_called_once()
        call_args = mock_storage.save_session.call_args[0][0]
        assert call_args.title == "New Session"
        assert call_args.user_id == "test_user"
        assert call_args.id is None  # Should be None for new sessions
        assert isinstance(call_args.created_at, datetime)
        assert isinstance(call_args.last_activity, datetime)

        # Verify return value
        assert result == expected_session

    def test_create_session_with_default_user(self, session_manager, mock_storage):
        """Test creating session with default user_id."""
        expected_session = UserSession(
            id=1,
            user_id="default_user",
            title="Default Session",
        )
        mock_storage.save_session.return_value = expected_session

        result = session_manager.create_session("Default Session")

        # Verify default user_id is used
        call_args = mock_storage.save_session.call_args[0][0]
        assert call_args.user_id == "default_user"

    def test_get_all_sessions(self, session_manager, mock_storage):
        """Test retrieving all sessions for a user."""
        expected_sessions = [
            UserSession(id=1, user_id="test_user", title="Session 1"),
            UserSession(id=2, user_id="test_user", title="Session 2"),
        ]
        mock_storage.load_all_sessions.return_value = expected_sessions

        result = session_manager.get_all_sessions("test_user")

        mock_storage.load_all_sessions.assert_called_once_with("test_user")
        assert result == expected_sessions

    def test_get_all_sessions_default_user(self, session_manager, mock_storage):
        """Test retrieving all sessions with default user_id."""
        mock_storage.load_all_sessions.return_value = []

        session_manager.get_all_sessions()

        mock_storage.load_all_sessions.assert_called_once_with("default_user")

    def test_get_session_by_id_exists(self, session_manager, mock_storage, sample_session):
        """Test retrieving session by ID when it exists."""
        mock_storage.load_session.return_value = sample_session

        result = session_manager.get_session_by_id(1)

        mock_storage.load_session.assert_called_once_with(1)
        assert result == sample_session

    def test_get_session_by_id_not_exists(self, session_manager, mock_storage):
        """Test retrieving session by ID when it doesn't exist."""
        mock_storage.load_session.return_value = None

        result = session_manager.get_session_by_id(999)

        mock_storage.load_session.assert_called_once_with(999)
        assert result is None

    def test_delete_session_success(self, session_manager, mock_storage):
        """Test successful session deletion."""
        mock_storage.delete_session.return_value = True

        result = session_manager.delete_session(1)

        mock_storage.delete_session.assert_called_once_with(1)
        assert result is True

    def test_delete_session_failure(self, session_manager, mock_storage):
        """Test failed session deletion."""
        mock_storage.delete_session.return_value = False

        result = session_manager.delete_session(999)

        mock_storage.delete_session.assert_called_once_with(999)
        assert result is False

    def test_add_message_to_session(self, session_manager, mock_storage, sample_session):
        """Test adding a message to a session."""
        # Mock the storage save_session call
        mock_storage.save_session.return_value = sample_session

        session_manager.add_message_to_session(
            sample_session,
            "user",
            "Test message",
            {"key": "value"}
        )

        # Verify session.add_message was called (indirectly via conversation history)
        assert len(sample_session.conversation_history) == 1
        message = sample_session.conversation_history[0]
        assert message["role"] == "user"
        assert message["content"] == "Test message"
        assert message["metadata"] == {"key": "value"}
        assert "timestamp" in message

        # Verify storage.save_session was called
        mock_storage.save_session.assert_called_once_with(sample_session)

    def test_add_message_to_session_without_metadata(self, session_manager, mock_storage, sample_session):
        """Test adding a message without metadata."""
        mock_storage.save_session.return_value = sample_session

        session_manager.add_message_to_session(
            sample_session,
            "assistant",
            "Assistant response"
        )

        # Verify message was added correctly
        assert len(sample_session.conversation_history) == 1
        message = sample_session.conversation_history[0]
        assert message["role"] == "assistant"
        assert message["content"] == "Assistant response"
        assert message["metadata"] == {}

        mock_storage.save_session.assert_called_once_with(sample_session)

    def test_update_session_activity(self, session_manager, mock_storage, sample_session):
        """Test updating session's last activity."""
        original_activity = sample_session.last_activity
        mock_storage.save_session.return_value = sample_session

        session_manager.update_session_activity(sample_session)

        # Verify last_activity was updated
        assert sample_session.last_activity > original_activity
        
        # Verify storage was called
        mock_storage.save_session.assert_called_once_with(sample_session)

    def test_multiple_operations_session_workflow(self, session_manager, mock_storage):
        """Test a complete workflow with multiple operations."""
        # Mock responses for different operations
        created_session = UserSession(
            id=1,
            user_id="workflow_user",
            title="Workflow Session",
        )
        mock_storage.save_session.return_value = created_session
        mock_storage.load_session.return_value = created_session
        mock_storage.load_all_sessions.return_value = [created_session]
        mock_storage.delete_session.return_value = True

        # 1. Create session
        session = session_manager.create_session("Workflow Session", "workflow_user")
        assert session.id == 1

        # 2. Add messages
        session_manager.add_message_to_session(session, "user", "Hello")
        session_manager.add_message_to_session(session, "assistant", "Hi there!")

        # 3. Update activity
        session_manager.update_session_activity(session)

        # 4. Retrieve session
        retrieved = session_manager.get_session_by_id(1)
        assert retrieved == created_session

        # 5. Get all sessions
        all_sessions = session_manager.get_all_sessions("workflow_user")
        assert len(all_sessions) == 1

        # 6. Delete session
        deleted = session_manager.delete_session(1)
        assert deleted is True

        # Verify all storage calls were made
        assert mock_storage.save_session.call_count == 4  # create + 2 messages + update
        mock_storage.load_session.assert_called_with(1)
        mock_storage.load_all_sessions.assert_called_with("workflow_user")
        mock_storage.delete_session.assert_called_with(1)

    def test_error_handling_storage_exceptions(self, session_manager, mock_storage):
        """Test that storage exceptions are properly propagated."""
        # Mock storage to raise exception
        mock_storage.save_session.side_effect = Exception("Storage error")

        with pytest.raises(Exception, match="Storage error"):
            session_manager.create_session("Test Session")

        # Test other operations
        mock_storage.load_session.side_effect = Exception("Load error")
        with pytest.raises(Exception, match="Load error"):
            session_manager.get_session_by_id(1)

        mock_storage.delete_session.side_effect = Exception("Delete error")
        with pytest.raises(Exception, match="Delete error"):
            session_manager.delete_session(1)

    def test_session_state_consistency(self, session_manager, mock_storage):
        """Test that session state remains consistent across operations."""
        session = UserSession(
            user_id="consistency_user",
            title="Consistency Test",
        )
        
        # Mock storage to return the same session object
        mock_storage.save_session.return_value = session

        # Add multiple messages
        session_manager.add_message_to_session(session, "user", "Message 1")
        session_manager.add_message_to_session(session, "assistant", "Response 1")
        session_manager.add_message_to_session(session, "user", "Message 2")

        # Verify conversation history accumulated correctly
        assert len(session.conversation_history) == 3
        assert session.conversation_history[0]["content"] == "Message 1"
        assert session.conversation_history[1]["content"] == "Response 1"
        assert session.conversation_history[2]["content"] == "Message 2"

        # Verify storage was called for each message
        assert mock_storage.save_session.call_count == 3

    def test_edge_cases(self, session_manager, mock_storage):
        """Test edge cases and boundary conditions."""
        # Empty title
        mock_storage.save_session.return_value = UserSession(
            id=1, user_id="test", title=""
        )
        result = session_manager.create_session("")
        assert result.title == ""

        # Very long title
        long_title = "A" * 1000
        mock_storage.save_session.return_value = UserSession(
            id=2, user_id="test", title=long_title
        )
        result = session_manager.create_session(long_title)
        assert result.title == long_title

        # Special characters in user_id
        special_user = "user@domain.com"
        mock_storage.save_session.return_value = UserSession(
            id=3, user_id=special_user, title="Test"
        )
        result = session_manager.create_session("Test", special_user)
        assert result.user_id == special_user

    def test_datetime_handling(self, session_manager, mock_storage):
        """Test that datetime objects are handled correctly."""
        session = UserSession(user_id="time_user", title="Time Test")
        mock_storage.save_session.return_value = session

        # Create session and check timestamps
        result = session_manager.create_session("Time Test", "time_user")
        
        call_args = mock_storage.save_session.call_args[0][0]
        assert isinstance(call_args.created_at, datetime)
        assert isinstance(call_args.last_activity, datetime)
        
        # Update activity and verify timestamp changes
        original_activity = call_args.last_activity
        session_manager.update_session_activity(call_args)
        
        assert call_args.last_activity > original_activity

    def test_integration_with_real_storage(self):
        """Test SessionManager with actual SessionStorage (integration-style test)."""
        # This test uses real storage but with in-memory database
        import tempfile
        from pathlib import Path
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create manager with real storage
            storage = SessionStorage(db_path=db_path)
            manager = SessionManager(storage=storage)
            
            # Test full workflow
            session = manager.create_session("Integration Test")
            assert session.id is not None
            
            manager.add_message_to_session(session, "user", "Test message")
            assert len(session.conversation_history) == 1
            
            retrieved = manager.get_session_by_id(session.id)
            assert retrieved.title == "Integration Test"
            assert len(retrieved.conversation_history) == 1
            
            all_sessions = manager.get_all_sessions()
            assert len(all_sessions) == 1
            
            deleted = manager.delete_session(session.id)
            assert deleted is True
            
            # Verify session is gone
            assert manager.get_session_by_id(session.id) is None
        finally:
            Path(db_path).unlink(missing_ok=True)