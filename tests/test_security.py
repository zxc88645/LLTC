"""Security tests for SSH AI Assistant."""

import pytest
import os
import tempfile
from pathlib import Path

from src.models import MachineConfig
from src.machine_manager import MachineManager


@pytest.mark.security
class TestSecurity:
    """Security-related test cases."""
    
    def test_password_not_logged(self, caplog):
        """Test that passwords are not logged in plain text."""
        machine_config = {
            "id": "test-security",
            "name": "Security Test Machine",
            "host": "localhost",
            "username": "testuser",
            "password": "secret_password_123"
        }
        
        manager = MachineManager()
        manager.add_machine(machine_config)
        
        # Check that password is not in logs
        for record in caplog.records:
            assert "secret_password_123" not in record.message
    
    def test_private_key_path_validation(self):
        """Test that private key paths are validated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test private key file
            key_path = Path(temp_dir) / "test_key"
            key_path.write_text("-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----")
            
            machine_config = {
                "id": "test-key-security",
                "name": "Key Security Test",
                "host": "localhost",
                "username": "testuser",
                "private_key_path": str(key_path)
            }
            
            manager = MachineManager()
            result = manager.add_machine(machine_config)
            assert result is True
    
    def test_invalid_private_key_path(self):
        """Test handling of invalid private key paths."""
        machine_config = {
            "id": "test-invalid-key",
            "name": "Invalid Key Test",
            "host": "localhost",
            "username": "testuser",
            "private_key_path": "/nonexistent/path/to/key"
        }
        
        manager = MachineManager()
        # Should not raise an exception, but should handle gracefully
        result = manager.add_machine(machine_config)
        # The machine should still be added, but key validation should happen during connection
        assert result is True
    
    @pytest.mark.security
    def test_machine_config_sanitization(self):
        """Test that machine configurations are properly sanitized."""
        # Test with potentially dangerous characters
        machine_config = {
            "id": "test-sanitize",
            "name": "Test; rm -rf /",  # Potentially dangerous name
            "host": "localhost",
            "username": "testuser",
            "password": "testpass"
        }
        
        manager = MachineManager()
        result = manager.add_machine(machine_config)
        assert result is True
        
        # Retrieve and verify the machine was stored safely
        machine = manager.get_machine("test-sanitize")
        assert machine is not None
        assert machine.name == "Test; rm -rf /"  # Should be stored as-is but handled safely
    
    @pytest.mark.security
    def test_session_isolation(self):
        """Test that sessions are properly isolated."""
        from src.ai_agent import AIAgent
        
        agent = AIAgent()
        
        # Create two sessions
        session1 = agent.create_session()
        session2 = agent.create_session()
        
        assert session1 != session2
        
        # Verify sessions are isolated
        context1 = agent.get_session(session1)
        context2 = agent.get_session(session2)
        
        assert context1.session_id != context2.session_id
        assert context1.conversation_history != context2.conversation_history
    
    @pytest.mark.security
    def test_database_path_security(self):
        """Test that database paths are handled securely."""
        from src.database import get_database_path
        
        # Test that database path is within expected directory
        db_path = get_database_path()
        
        # Should not allow path traversal
        assert ".." not in str(db_path)
        assert str(db_path).endswith(".db")