"""Tests for the web application."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Set up test environment
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

from src.web_app import app
from src.database import init_database, get_database_path


@pytest.fixture
def client():
    """Create test client."""
    # Use temporary database for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set database path to temp directory
        os.environ['DATABASE_DIR'] = temp_dir
        
        # Initialize test database
        init_database()
        
        # Create test client
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def sample_machine():
    """Sample machine configuration for testing."""
    return {
        "name": "Test Machine",
        "host": "localhost",
        "port": 22,
        "username": "testuser",
        "password": "testpass",
        "description": "Test machine for unit tests"
    }


class TestWebApp:
    """Test cases for web application."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]  # Allow degraded status
        assert "timestamp" in data
        # Check if components are included in enhanced health check
        if "components" in data:
            assert isinstance(data["components"], dict)
    
    def test_home_page(self, client):
        """Test home page renders."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_create_session(self, client):
        """Test session creation."""
        response = client.post("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
    
    def test_get_session(self, client):
        """Test getting session information."""
        # Create session first
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["session_id"]
        
        # Get session info
        response = client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["selected_machine"] is None
        assert "created_at" in data
        assert "last_activity" in data
        assert "conversation_history" in data
    
    def test_get_nonexistent_session(self, client):
        """Test getting non-existent session."""
        response = client.get("/api/sessions/nonexistent")
        assert response.status_code == 404
    
    def test_list_machines_empty(self, client):
        """Test listing machines when none exist."""
        response = client.get("/api/machines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_machine(self, client, sample_machine):
        """Test creating a machine configuration."""
        # Note: This will fail connection test, but we're testing the API structure
        response = client.post("/api/machines", json=sample_machine)
        # Expect 400 because connection will fail to localhost
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_create_machine_invalid_data(self, client):
        """Test creating machine with invalid data."""
        invalid_machine = {
            "name": "",  # Empty name should fail validation
            "host": "localhost"
            # Missing required fields
        }
        response = client.post("/api/machines", json=invalid_machine)
        assert response.status_code == 422  # Validation error
    
    def test_get_nonexistent_machine(self, client):
        """Test getting non-existent machine."""
        response = client.get("/api/machines/nonexistent")
        assert response.status_code == 404
    
    def test_update_nonexistent_machine(self, client):
        """Test updating non-existent machine."""
        updates = {"name": "Updated Name"}
        response = client.put("/api/machines/nonexistent", json=updates)
        assert response.status_code == 404
    
    def test_delete_nonexistent_machine(self, client):
        """Test deleting non-existent machine."""
        response = client.delete("/api/machines/nonexistent")
        assert response.status_code == 404
    
    def test_search_machines_empty(self, client):
        """Test searching machines when none exist."""
        response = client.get("/api/machines/search/test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_select_machine_invalid_session(self, client):
        """Test selecting machine with invalid session."""
        response = client.post("/api/sessions/invalid/select-machine/machine123")
        assert response.status_code == 404
    
    def test_chat_page_invalid_session(self, client):
        """Test chat page with invalid session."""
        response = client.get("/chat/invalid")
        assert response.status_code == 404


class TestWebSocketConnection:
    """Test WebSocket functionality."""
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection establishment."""
        # Create session first
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["session_id"]
        
        # Test WebSocket connection
        with client.websocket_connect(f"/ws/{session_id}") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data
    
    def test_websocket_chat_message_no_machine(self, client):
        """Test sending chat message without selected machine."""
        # Create session first
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["session_id"]
        
        # Test WebSocket connection
        with client.websocket_connect(f"/ws/{session_id}") as websocket:
            # Send chat message
            websocket.send_json({
                "type": "chat_message",
                "message": "Hello"
            })
            
            # Should receive acknowledgment
            ack_data = websocket.receive_json()
            assert ack_data["type"] == "message_received"
            assert ack_data["message"] == "Hello"
            
            # Should receive error response
            response_data = websocket.receive_json()
            assert response_data["type"] == "ai_response"
            assert response_data["success"] is False
            assert "No machine selected" in response_data["error"]


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_database_initialization(self):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set database path to temp directory
            original_env = os.environ.get('DATABASE_DIR')
            os.environ['DATABASE_DIR'] = temp_dir
            
            try:
                # Initialize database
                init_database()
                
                # Check if database file was created
                db_path = Path(temp_dir) / "ssh_ai.db"
                assert db_path.exists()
                
                # Check file permissions (should be readable/writable by owner only)
                stat = db_path.stat()
                # On Unix systems, check that it's not world-readable
                if hasattr(stat, 'st_mode'):
                    mode = stat.st_mode & 0o777
                    assert mode == 0o600
                    
            finally:
                # Restore original environment
                if original_env:
                    os.environ['DATABASE_DIR'] = original_env
                elif 'DATABASE_DIR' in os.environ:
                    del os.environ['DATABASE_DIR']


if __name__ == "__main__":
    pytest.main([__file__])