"""SSH connection and command execution management."""

import paramiko
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

from .models import MachineConfig, CommandResult


logger = logging.getLogger(__name__)


class SSHManager:
    """Manages SSH connections and command execution."""
    
    def __init__(self):
        self.connections: Dict[str, paramiko.SSHClient] = {}
    
    def _create_ssh_client(self, machine: MachineConfig) -> paramiko.SSHClient:
        """Create and configure an SSH client."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client
    
    def _connect(self, machine: MachineConfig) -> paramiko.SSHClient:
        """Establish SSH connection to a machine."""
        client = self._create_ssh_client(machine)
        
        try:
            # Prepare connection parameters
            connect_params = {
                'hostname': machine.host,
                'port': machine.port,
                'username': machine.username,
                'timeout': 30
            }
            
            # Add authentication method
            if machine.private_key_path:
                connect_params['key_filename'] = machine.private_key_path
            elif machine.password:
                connect_params['password'] = machine.password
            else:
                raise ValueError("No authentication method provided")
            
            client.connect(**connect_params)
            logger.info(f"Successfully connected to {machine.host}:{machine.port}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to connect to {machine.host}:{machine.port}: {e}")
            client.close()
            raise
    
    @contextmanager
    def get_connection(self, machine: MachineConfig):
        """Context manager for SSH connections."""
        client = None
        try:
            client = self._connect(machine)
            yield client
        finally:
            if client:
                client.close()
    
    def execute_command(self, machine: MachineConfig, command: str, timeout: int = 300) -> CommandResult:
        """Execute a command on the remote machine."""
        start_time = time.time()
        
        try:
            with self.get_connection(machine) as client:
                logger.info(f"Executing command on {machine.host}: {command}")
                
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
                
                # Read output
                stdout_data = stdout.read().decode('utf-8', errors='replace')
                stderr_data = stderr.read().decode('utf-8', errors='replace')
                exit_code = stdout.channel.recv_exit_status()
                
                execution_time = time.time() - start_time
                
                result = CommandResult(
                    command=command,
                    stdout=stdout_data,
                    stderr=stderr_data,
                    exit_code=exit_code,
                    execution_time=execution_time
                )
                
                logger.info(f"Command completed with exit code {exit_code} in {execution_time:.2f}s")
                return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {e}")
            
            return CommandResult(
                command=command,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time
            )
    
    def test_connection(self, machine: MachineConfig) -> bool:
        """Test SSH connection to a machine."""
        try:
            with self.get_connection(machine) as client:
                # Execute a simple command to verify connection
                stdin, stdout, stderr = client.exec_command('echo "connection_test"', timeout=10)
                output = stdout.read().decode('utf-8').strip()
                return output == "connection_test"
        except Exception as e:
            logger.error(f"Connection test failed for {machine.host}: {e}")
            return False
    
    def get_system_info(self, machine: MachineConfig) -> Dict[str, Any]:
        """Get basic system information from the machine."""
        info = {}
        
        # Get OS information
        os_result = self.execute_command(machine, "uname -a")
        if os_result.success:
            info['os'] = os_result.stdout.strip()
        
        # Get uptime
        uptime_result = self.execute_command(machine, "uptime")
        if uptime_result.success:
            info['uptime'] = uptime_result.stdout.strip()
        
        # Get disk usage
        disk_result = self.execute_command(machine, "df -h")
        if disk_result.success:
            info['disk_usage'] = disk_result.stdout.strip()
        
        # Get memory usage
        mem_result = self.execute_command(machine, "free -h")
        if mem_result.success:
            info['memory_usage'] = mem_result.stdout.strip()
        
        return info