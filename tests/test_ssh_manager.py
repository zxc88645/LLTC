"""Tests for SSH manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ssh_manager import SSHManager
from src.models import MachineConfig, CommandResult


class TestSSHManager:
    """Test SSHManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.ssh_manager = SSHManager()
        self.test_machine = MachineConfig(
            id="test-machine",
            name="Test Machine",
            host="test.example.com",
            username="testuser",
            password="testpass",
        )
    
    @patch("src.ssh_manager.paramiko.SSHClient")
    def test_execute_command_success(self, mock_ssh_client):
        """Test successful command execution."""
        # Mock SSH client and its methods
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Mock command execution
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        mock_stdout.read.return_value = b"Hello World\n"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Execute command
        result = self.ssh_manager.execute_command(self.test_machine, "echo 'Hello World'")
        
        # Verify result
        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.stdout == "Hello World\n"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.command == "echo 'Hello World'"
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_execute_command_failure(self, mock_ssh_client):
        """Test failed command execution."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Mock command execution with failure
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b"command not found\n"
        mock_stdout.channel.recv_exit_status.return_value = 127
        
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Execute command
        result = self.ssh_manager.execute_command(self.test_machine, "invalid_command")
        
        # Verify result
        assert result.success is False
        assert result.stdout == ""
        assert result.stderr == "command not found\n"
        assert result.exit_code == 127
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_connection_error(self, mock_ssh_client):
        """Test SSH connection error handling."""
        # Mock SSH client to raise connection error
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection refused")
        
        # Execute command
        result = self.ssh_manager.execute_command(self.test_machine, "echo test")
        
        # Verify error handling
        assert result.success is False
        assert result.exit_code == -1
        assert "Connection refused" in result.stderr
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_test_connection_success(self, mock_ssh_client):
        """Test successful connection test."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Mock successful connection test
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        mock_stdout.read.return_value = b"connection_test\n"
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Test connection
        result = self.ssh_manager.test_connection(self.test_machine)
        
        assert result is True
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_test_connection_failure(self, mock_ssh_client):
        """Test failed connection test."""
        # Mock SSH client to raise exception
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection failed")
        
        # Test connection
        result = self.ssh_manager.test_connection(self.test_machine)
        
        assert result is False
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_get_system_info(self, mock_ssh_client):
        """Test getting system information."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        
        # Mock multiple command executions
        def mock_exec_command(command, timeout=None):
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            
            if "uname -a" in command:
                mock_stdout.read.return_value = b"Linux test 5.4.0 x86_64\n"
                mock_stdout.channel.recv_exit_status.return_value = 0
            elif "uptime" in command:
                mock_stdout.read.return_value = b"up 1 day, 2:30\n"
                mock_stdout.channel.recv_exit_status.return_value = 0
            elif "df -h" in command:
                mock_stdout.read.return_value = b"/dev/sda1  20G  10G  9G  53% /\n"
                mock_stdout.channel.recv_exit_status.return_value = 0
            elif "free -h" in command:
                mock_stdout.read.return_value = b"Mem: 8G 4G 4G\n"
                mock_stdout.channel.recv_exit_status.return_value = 0
            else:
                mock_stdout.read.return_value = b""
                mock_stdout.channel.recv_exit_status.return_value = 1
            
            mock_stderr.read.return_value = b""
            return mock_stdin, mock_stdout, mock_stderr
        
        mock_client.exec_command.side_effect = mock_exec_command
        
        # Get system info
        info = self.ssh_manager.get_system_info(self.test_machine)
        
        # Verify system info
        assert 'os' in info
        assert 'uptime' in info
        assert 'disk_usage' in info
        assert 'memory_usage' in info
        assert "Linux test" in info['os']