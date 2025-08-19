"""Integration tests for complete workflows."""

import pytest
import tempfile
import shutil
from unittest.mock import patch, Mock
from pathlib import Path

from src.ai_agent import AIAgent
from src.machine_manager import MachineManager
from src.models import MachineConfig, CommandResult


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete user workflows from start to finish."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_complete_session_workflow(self, mock_ssh_client):
        """Test complete session from creation to command execution."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Mock successful connection
        mock_client.connect.return_value = None
        
        # Mock command execution
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.read.return_value = b"Linux test-server 5.4.0\n"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Step 1: Create session
        session_id = self.agent.create_session()
        assert session_id is not None
        
        # Step 2: Add machine
        machine_config = {
            "id": "test-server",
            "name": "Test Server",
            "host": "test.example.com",
            "username": "testuser",
            "password": "testpass"
        }
        
        add_result = self.agent.add_machine(machine_config)
        assert add_result["success"] is True
        
        # Step 3: Select machine
        select_result = self.agent.select_machine(session_id, "test-server")
        assert select_result["success"] is True
        
        # Step 4: Execute command
        command_result = self.agent.process_command(session_id, "幫我查看這台作業系統版本")
        assert command_result["success"] is True
        assert "results" in command_result
        assert len(command_result["results"]) > 0
        
        # Step 5: Verify conversation history
        history = self.agent.get_conversation_history(session_id)
        assert len(history) > 0
        assert any("作業系統版本" in entry.get("user_message", "") for entry in history)
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_multi_machine_workflow(self, mock_ssh_client):
        """Test workflow with multiple machines."""
        # Setup mock
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.return_value = None
        
        # Create session
        session_id = self.agent.create_session()
        
        # Add multiple machines
        machines = [
            {
                "id": "web-server",
                "name": "Web Server",
                "host": "web.example.com",
                "username": "webuser",
                "password": "webpass"
            },
            {
                "id": "db-server", 
                "name": "Database Server",
                "host": "db.example.com",
                "username": "dbuser",
                "password": "dbpass"
            }
        ]
        
        for machine in machines:
            result = self.agent.add_machine(machine)
            assert result["success"] is True
        
        # List machines
        machine_list = self.agent.list_machines()
        assert len(machine_list) == 2
        
        # Test switching between machines
        for machine in machines:
            select_result = self.agent.select_machine(session_id, machine["id"])
            assert select_result["success"] is True
            
            # Verify correct machine is selected
            context = self.agent.get_session(session_id)
            assert context.selected_machine == machine["id"]
    
    def test_error_handling_workflow(self):
        """Test error handling in complete workflow."""
        # Create session
        session_id = self.agent.create_session()
        
        # Try to execute command without selecting machine
        result = self.agent.process_command(session_id, "check os version")
        assert result["success"] is False
        assert "No machine selected" in result["error"]
        
        # Try to select non-existent machine
        select_result = self.agent.select_machine(session_id, "nonexistent")
        assert select_result["success"] is False
        assert "Machine not found" in select_result["error"]
        
        # Try operations with invalid session
        invalid_result = self.agent.process_command("invalid-session", "test")
        assert invalid_result["success"] is False
        assert "Invalid session" in invalid_result["error"]


@pytest.mark.integration
class TestPersistenceWorkflow:
    """Test data persistence across sessions."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_machine_persistence(self, mock_ssh_client):
        """Test that machine configurations persist across agent instances."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.return_value = None
        
        # Create first agent instance and add machine
        agent1 = AIAgent(config_dir=self.temp_dir)
        
        machine_config = {
            "id": "persistent-machine",
            "name": "Persistent Machine",
            "host": "persistent.example.com",
            "username": "persistuser",
            "password": "persistpass"
        }
        
        result = agent1.add_machine(machine_config)
        assert result["success"] is True
        
        # Create second agent instance and verify machine exists
        agent2 = AIAgent(config_dir=self.temp_dir)
        
        machines = agent2.list_machines()
        assert len(machines) == 1
        assert machines[0]["id"] == "persistent-machine"
        assert machines[0]["name"] == "Persistent Machine"
    
    def test_password_encryption_persistence(self):
        """Test that passwords remain encrypted when persisted."""
        # Create machine manager
        manager = MachineManager(config_dir=self.temp_dir)
        
        # Add machine with password
        machine = MachineConfig(
            id="secure-machine",
            name="Secure Machine", 
            host="secure.example.com",
            username="secureuser",
            password="supersecret123"
        )
        
        manager.add_machine(machine)
        
        # Check that password is encrypted in storage
        config_file = Path(self.temp_dir) / "machines.json"
        assert config_file.exists()
        
        # Read raw file content
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Password should not appear in plain text
        assert "supersecret123" not in content
        
        # But should be decryptable when retrieved
        retrieved = manager.get_machine("secure-machine")
        assert retrieved.password == "supersecret123"


@pytest.mark.integration
@pytest.mark.slow
class TestConcurrentOperations:
    """Test concurrent operations and thread safety."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_concurrent_sessions(self):
        """Test multiple concurrent sessions."""
        import threading
        import time
        
        sessions = []
        results = []
        
        def create_session():
            session_id = self.agent.create_session()
            sessions.append(session_id)
            
            # Simulate some work
            time.sleep(0.1)
            
            context = self.agent.get_session(session_id)
            results.append(context is not None)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_session)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all sessions were created successfully
        assert len(sessions) == 5
        assert all(results)
        assert len(set(sessions)) == 5  # All session IDs should be unique
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_concurrent_machine_operations(self, mock_ssh_client):
        """Test concurrent machine operations."""
        import threading
        
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.return_value = None
        
        results = []
        
        def add_machine(machine_id):
            machine_config = {
                "id": f"machine-{machine_id}",
                "name": f"Machine {machine_id}",
                "host": f"host{machine_id}.example.com",
                "username": f"user{machine_id}",
                "password": f"pass{machine_id}"
            }
            
            result = self.agent.add_machine(machine_config)
            results.append(result["success"])
        
        # Create multiple threads to add machines concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_machine, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all machines were added successfully
        assert all(results)
        
        # Verify all machines exist
        machines = self.agent.list_machines()
        assert len(machines) == 3