"""Tests for AI agent."""

import pytest
from unittest.mock import Mock, patch
from src.ai_agent import AIAgent
from src.models import MachineConfig, CommandResult, UserIntent


class TestAIAgent:
    """Test AIAgent class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = AIAgent()
        self.test_machine = MachineConfig(
            id="test-machine",
            name="Test Machine",
            host="test.example.com",
            username="testuser",
            password="testpass"
        )
    
    def test_create_session(self):
        """Test creating a new session."""
        session_id = self.agent.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        
        context = self.agent.get_session(session_id)
        assert context is not None
        assert context.session_id == session_id
    
    @patch.object(AIAgent, '_execute_intent')
    def test_process_command_success(self, mock_execute):
        """Test successful command processing."""
        # Setup
        session_id = self.agent.create_session()
        self.agent.machine_manager.add_machine(self.test_machine)
        self.agent.select_machine(session_id, "test-machine")
        
        # Mock command execution
        mock_result = CommandResult(
            command="uname -a",
            stdout="Linux test 5.4.0\n",
            stderr="",
            exit_code=0,
            execution_time=0.1
        )
        mock_execute.return_value = [mock_result]
        
        # Process command
        result = self.agent.process_command(session_id, "幫我查看這台作業系統版本")
        
        # Verify result
        assert result["success"] is True
        assert "intent" in result
        assert "results" in result
        assert "summary" in result
        assert len(result["results"]) == 1
    
    def test_process_command_no_machine_selected(self):
        """Test command processing without machine selection."""
        session_id = self.agent.create_session()
        
        result = self.agent.process_command(session_id, "check os version")
        
        assert result["success"] is False
        assert "No machine selected" in result["error"]
    
    def test_process_command_unknown_intent(self):
        """Test processing unknown command."""
        session_id = self.agent.create_session()
        self.agent.machine_manager.add_machine(self.test_machine)
        self.agent.select_machine(session_id, "test-machine")
        
        result = self.agent.process_command(session_id, "do something completely random")
        
        assert result["success"] is False
        assert "don't understand" in result["error"]
        assert "suggestions" in result or "available_commands" in result
    
    @patch('src.ai_agent.SSHManager.test_connection')
    def test_select_machine_success(self, mock_test_connection):
        """Test successful machine selection."""
        mock_test_connection.return_value = True
        
        session_id = self.agent.create_session()
        self.agent.machine_manager.add_machine(self.test_machine)
        
        result = self.agent.select_machine(session_id, "test-machine")
        
        assert result["success"] is True
        assert result["machine"]["id"] == "test-machine"
        assert result["machine"]["name"] == "Test Machine"
    
    @patch('src.ai_agent.SSHManager.test_connection')
    def test_select_machine_connection_failed(self, mock_test_connection):
        """Test machine selection with connection failure."""
        mock_test_connection.return_value = False
        
        session_id = self.agent.create_session()
        self.agent.machine_manager.add_machine(self.test_machine)
        
        result = self.agent.select_machine(session_id, "test-machine")
        
        assert result["success"] is False
        assert "Cannot connect" in result["error"]
    
    def test_select_nonexistent_machine(self):
        """Test selecting a non-existent machine."""
        session_id = self.agent.create_session()
        
        result = self.agent.select_machine(session_id, "nonexistent-machine")
        
        assert result["success"] is False
        assert "Machine not found" in result["error"]
    
    @patch('src.ai_agent.SSHManager.test_connection')
    def test_add_machine_success(self, mock_test_connection):
        """Test successful machine addition."""
        mock_test_connection.return_value = True
        
        machine_config = {
            "id": "new-machine",
            "name": "New Machine",
            "host": "new.example.com",
            "username": "newuser",
            "password": "newpass"
        }
        
        result = self.agent.add_machine(machine_config)
        
        assert result["success"] is True
        assert "machine_id" in result
        
        # Verify machine was added
        machines = self.agent.list_machines()
        assert len(machines) == 1
        assert machines[0]["id"] == "new-machine"
    
    @patch('src.ai_agent.SSHManager.test_connection')
    def test_add_machine_connection_failed(self, mock_test_connection):
        """Test machine addition with connection failure."""
        mock_test_connection.return_value = False
        
        machine_config = {
            "id": "bad-machine",
            "name": "Bad Machine",
            "host": "bad.example.com",
            "username": "baduser",
            "password": "badpass"
        }
        
        result = self.agent.add_machine(machine_config)
        
        assert result["success"] is False
        assert "Cannot connect" in result["error"]
    
    def test_list_machines(self):
        """Test listing machines."""
        # Add test machines
        machine1 = MachineConfig(
            id="machine1",
            name="Machine 1",
            host="host1.com",
            username="user1"
        )
        machine2 = MachineConfig(
            id="machine2",
            name="Machine 2",
            host="host2.com",
            username="user2"
        )
        
        self.agent.machine_manager.add_machine(machine1)
        self.agent.machine_manager.add_machine(machine2)
        
        machines = self.agent.list_machines()
        
        assert len(machines) == 2
        machine_ids = [m["id"] for m in machines]
        assert "machine1" in machine_ids
        assert "machine2" in machine_ids
    
    def test_remove_machine(self):
        """Test removing a machine."""
        self.agent.machine_manager.add_machine(self.test_machine)
        
        result = self.agent.remove_machine("test-machine")
        assert result["success"] is True
        
        # Verify removal
        machines = self.agent.list_machines()
        assert len(machines) == 0
    
    def test_get_conversation_history(self):
        """Test getting conversation history."""
        session_id = self.agent.create_session()
        
        history = self.agent.get_conversation_history(session_id)
        assert history is not None
        assert len(history) == 0  # Initially empty
    
    def test_invalid_session(self):
        """Test operations with invalid session."""
        result = self.agent.process_command("invalid-session", "test command")
        assert result["success"] is False
        assert "Invalid session" in result["error"]
        
        result = self.agent.select_machine("invalid-session", "test-machine")
        assert result["success"] is False
        assert "Invalid session" in result["error"]