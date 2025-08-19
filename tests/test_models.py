"""Tests for data models."""

import pytest
from datetime import datetime
from src.models import MachineConfig, CommandResult, UserIntent, ConversationContext


class TestMachineConfig:
    """Test MachineConfig model."""
    
    def test_machine_config_creation(self):
        """Test creating a machine configuration."""
        config = MachineConfig(
            id="test-machine",
            name="Test Machine",
            host="192.168.1.100",
            username="testuser",
            password="testpass",
        )
        
        assert config.id == "test-machine"
        assert config.name == "Test Machine"
        assert config.host == "192.168.1.100"
        assert config.port == 22  # default value
        assert config.username == "testuser"
        assert config.password == "testpass"
    
    def test_machine_config_with_key(self):
        """Test machine config with private key."""
        config = MachineConfig(
            id="key-machine",
            name="Key Machine",
            host="example.com",
            username="keyuser",
            private_key_path="/path/to/key",
        )
        
        assert config.private_key_path == "/path/to/key"
        assert config.password is None


class TestCommandResult:
    """Test CommandResult model."""
    
    def test_successful_command_result(self):
        """Test successful command result."""
        result = CommandResult(
            command="echo 'hello'",
            stdout="hello\n",
            stderr="",
            exit_code=0,
            execution_time=0.1,
        )
        
        assert result.success is True
        assert result.command == "echo 'hello'"
        assert result.stdout == "hello\n"
    
    def test_failed_command_result(self):
        """Test failed command result."""
        result = CommandResult(
            command="invalid_command",
            stdout="",
            stderr="command not found",
            exit_code=127,
            execution_time=0.05,
        )
        
        assert result.success is False
        assert result.exit_code == 127


class TestUserIntent:
    """Test UserIntent model."""
    
    def test_user_intent_creation(self):
        """Test creating user intent."""
        intent = UserIntent(
            action="check_os_version",
            parameters={"commands": ["uname -a"]},
            confidence=0.9,
            original_text="check os version",
        )
        
        assert intent.action == "check_os_version"
        assert intent.confidence == 0.9
        assert "commands" in intent.parameters


class TestConversationContext:
    """Test ConversationContext model."""
    
    def test_conversation_context_creation(self):
        """Test creating conversation context."""
        context = ConversationContext(session_id="test-session")
        
        assert context.session_id == "test-session"
        assert context.selected_machine is None
        assert len(context.conversation_history) == 0