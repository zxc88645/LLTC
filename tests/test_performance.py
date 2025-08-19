"""Performance tests for SSH AI Assistant."""

import pytest
import time
import threading
from unittest.mock import patch, Mock
import tempfile
import shutil

from src.ai_agent import AIAgent
from src.machine_manager import MachineManager
from src.command_interpreter import CommandInterpreter


@pytest.mark.performance
class TestCommandInterpretationPerformance:
    """Test command interpretation performance."""
    
    def setup_method(self):
        """Setup test environment."""
        self.interpreter = CommandInterpreter()
    
    def test_single_command_interpretation_speed(self, performance_monitor):
        """Test speed of single command interpretation."""
        performance_monitor.start()
        
        # Test command interpretation
        intent = self.interpreter.interpret_command("幫我查看這台作業系統版本")
        
        performance_monitor.stop()
        
        # Verify result
        assert intent.action == "check_os_version"
        
        # Performance assertions
        report = performance_monitor.get_report()
        assert report['execution_time'] < 0.1  # Should complete in under 100ms
        assert report['peak_memory_mb'] < 50   # Should use less than 50MB
    
    def test_batch_command_interpretation_performance(self, chinese_commands, performance_monitor):
        """Test performance with multiple commands."""
        performance_monitor.start()
        
        results = []
        for command in chinese_commands:
            intent = self.interpreter.interpret_command(command)
            results.append(intent)
        
        performance_monitor.stop()
        
        # Verify all commands were processed
        assert len(results) == len(chinese_commands)
        assert all(result.confidence > 0 for result in results)
        
        # Performance assertions
        report = performance_monitor.get_report()
        avg_time_per_command = report['execution_time'] / len(chinese_commands)
        assert avg_time_per_command < 0.05  # Average under 50ms per command
        assert report['peak_memory_mb'] < 100  # Should use less than 100MB total


@pytest.mark.performance
class TestSessionManagementPerformance:
    """Test session management performance."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_session_creation_performance(self, performance_monitor):
        """Test session creation speed."""
        performance_monitor.start()
        
        # Create multiple sessions
        sessions = []
        for _ in range(100):
            session_id = self.agent.create_session()
            sessions.append(session_id)
        
        performance_monitor.stop()
        
        # Verify all sessions created
        assert len(sessions) == 100
        assert len(set(sessions)) == 100  # All unique
        
        # Performance assertions
        report = performance_monitor.get_report()
        avg_time_per_session = report['execution_time'] / 100
        assert avg_time_per_session < 0.01  # Under 10ms per session
        assert report['peak_memory_mb'] < 200  # Under 200MB for 100 sessions
    
    def test_concurrent_session_performance(self):
        """Test concurrent session creation performance."""
        import concurrent.futures
        
        start_time = time.time()
        
        def create_session():
            return self.agent.create_session()
        
        # Create sessions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_session) for _ in range(50)]
            sessions = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify results
        assert len(sessions) == 50
        assert len(set(sessions)) == 50  # All unique
        
        # Performance assertions
        assert execution_time < 2.0  # Should complete in under 2 seconds
        avg_time_per_session = execution_time / 50
        assert avg_time_per_session < 0.04  # Under 40ms per session on average


@pytest.mark.performance
class TestMachineManagementPerformance:
    """Test machine management performance."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MachineManager(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_machine_addition_performance(self, sample_machines, performance_monitor):
        """Test machine addition performance."""
        performance_monitor.start()
        
        # Add multiple machines
        for machine in sample_machines:
            success = self.manager.add_machine(machine)
            assert success is True
        
        performance_monitor.stop()
        
        # Verify machines were added
        machines = self.manager.list_machines()
        assert len(machines) == len(sample_machines)
        
        # Performance assertions
        report = performance_monitor.get_report()
        avg_time_per_machine = report['execution_time'] / len(sample_machines)
        assert avg_time_per_machine < 0.1  # Under 100ms per machine
    
    def test_machine_search_performance(self, performance_monitor):
        """Test machine search performance with large dataset."""
        # Add many machines
        from tests.conftest import MachineConfigFactory
        machines = MachineConfigFactory.create_batch(100)
        
        for machine in machines:
            self.manager.add_machine(machine)
        
        performance_monitor.start()
        
        # Perform searches
        search_terms = ["test", "server", "prod", "dev", "web"]
        for term in search_terms:
            results = self.manager.search_machines(term)
            # Results may be empty, that's ok for performance testing
        
        performance_monitor.stop()
        
        # Performance assertions
        report = performance_monitor.get_report()
        avg_time_per_search = report['execution_time'] / len(search_terms)
        assert avg_time_per_search < 0.05  # Under 50ms per search


@pytest.mark.performance
@pytest.mark.slow
class TestMemoryUsagePerformance:
    """Test memory usage patterns."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_usage_with_many_sessions(self, performance_monitor):
        """Test memory usage with many active sessions."""
        performance_monitor.start()
        
        # Create many sessions
        sessions = []
        for i in range(200):
            session_id = self.agent.create_session()
            sessions.append(session_id)
            
            # Add some conversation history to each session
            context = self.agent.get_session(session_id)
            context.conversation_history.extend([
                {"user_message": f"Test message {j}", "ai_response": f"Response {j}"}
                for j in range(5)
            ])
        
        performance_monitor.stop()
        
        # Performance assertions
        report = performance_monitor.get_report()
        assert report['peak_memory_mb'] < 500  # Should stay under 500MB
        
        # Cleanup sessions to test memory release
        for session_id in sessions:
            if hasattr(self.agent, 'close_session'):
                self.agent.close_session(session_id)
    
    @patch('src.ssh_manager.paramiko.SSHClient')
    def test_memory_usage_with_command_execution(self, mock_ssh_client, performance_monitor):
        """Test memory usage during command execution."""
        # Mock SSH client
        mock_client = Mock()
        mock_ssh_client.return_value = mock_client
        mock_client.connect.return_value = None
        
        # Mock command with large output
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        large_output = "x" * 10000  # 10KB output
        mock_stdout.read.return_value = large_output.encode()
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Add machine and create session
        machine_config = {
            "id": "test-machine",
            "name": "Test Machine",
            "host": "test.example.com",
            "username": "testuser",
            "password": "testpass"
        }
        self.agent.add_machine(machine_config)
        session_id = self.agent.create_session()
        self.agent.select_machine(session_id, "test-machine")
        
        performance_monitor.start()
        
        # Execute multiple commands
        for i in range(20):
            result = self.agent.process_command(session_id, f"command {i}")
            assert result["success"] is True
        
        performance_monitor.stop()
        
        # Performance assertions
        report = performance_monitor.get_report()
        assert report['peak_memory_mb'] < 300  # Should stay under 300MB


@pytest.mark.performance
class TestDatabasePerformance:
    """Test database operation performance."""
    
    def test_database_initialization_performance(self, performance_monitor):
        """Test database initialization speed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            performance_monitor.start()
            
            # Initialize database multiple times
            from src.database import init_database
            import os
            
            original_env = os.environ.get('DATABASE_DIR')
            os.environ['DATABASE_DIR'] = temp_dir
            
            try:
                for i in range(5):
                    init_database()
            finally:
                if original_env:
                    os.environ['DATABASE_DIR'] = original_env
                elif 'DATABASE_DIR' in os.environ:
                    del os.environ['DATABASE_DIR']
            
            performance_monitor.stop()
            
            # Performance assertions
            report = performance_monitor.get_report()
            avg_time_per_init = report['execution_time'] / 5
            assert avg_time_per_init < 0.1  # Under 100ms per initialization


@pytest.mark.performance
class TestLoadTesting:
    """Load testing scenarios."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_high_frequency_requests(self):
        """Test handling high frequency requests."""
        import concurrent.futures
        import logging  # Import logging module for exception handling
        
        # Create session
        session_id = self.agent.create_session()
        
        start_time = time.time()
        
        def make_request():
            # Test various operations
            operations = [
                lambda: self.agent.create_session(),
                lambda: self.agent.list_machines(),
                lambda: self.agent.get_conversation_history(session_id),
            ]
            
            for op in operations:
                try:
                    op()
                except Exception as e:
                    logging.exception("Error during operation: %s", e)  # Log exception details
        
        # Execute many requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.exception("Error in future execution: %s", e)  # Log exception details
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 10.0  # Should complete in under 10 seconds
        requests_per_second = 300 / execution_time  # 100 requests * 3 operations each
        assert requests_per_second > 30  # Should handle at least 30 requests per second
                    pass  # Ignore errors for load testing
        
        # Execute many requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
def test_high_frequency_requests(self):
        """Test handling high frequency requests."""
        import concurrent.futures
        import logging  # Import logging module for exception handling
        
        # Create session
        session_id = self.agent.create_session()
        
        start_time = time.time()
        
        def make_request():
            # Test various operations
            operations = [
                lambda: self.agent.create_session(),
                lambda: self.agent.list_machines(),
                lambda: self.agent.get_conversation_history(session_id),
            ]
            
            for op in operations:
                try:
                    op()
                except Exception as e:
                    logging.exception("Error during operation: %s", e)  # Log exception details
        
        # Execute many requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.exception("Error in future execution: %s", e)  # Log exception details
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 10.0  # Should complete in under 10 seconds
        requests_per_second = 300 / execution_time  # 100 requests * 3 operations each
        assert requests_per_second > 30  # Should handle at least 30 requests per second
                    pass  # Ignore errors for load testing
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 10.0  # Should complete in under 10 seconds
        requests_per_second = 300 / execution_time  # 100 requests * 3 operations each
        assert requests_per_second > 30  # Should handle at least 30 requests per second