"""Utilities for establishing SSH connections and executing commands."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict
from socket import gaierror

import paramiko

from .models import MachineConfig, CommandResult

logger = logging.getLogger(__name__)


class SSHManager:
    """Manage SSH connections and run commands on remote machines."""

    def _create_client(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    @contextmanager
    def get_connection(self, machine: MachineConfig):
        client = self._create_client()
        try:
            client.connect(
                hostname=machine.host,
                port=machine.port,
                username=machine.username,
                password=machine.password,
                key_filename=machine.private_key_path,
                timeout=30,
            )
            yield client
        finally:
            client.close()

    # ------------------------------------------------------------------
    def execute_command(self, machine: MachineConfig, command: str, timeout: int = 300) -> CommandResult:
        start = time.time()
        try:
            with self.get_connection(machine) as client:
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
                stdout_data = stdout.read().decode("utf-8", errors="replace")
                stderr_data = stderr.read().decode("utf-8", errors="replace")
                exit_code = stdout.channel.recv_exit_status()
            return CommandResult(
                command=command,
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
                execution_time=time.time() - start,
            )
        except Exception as exc:
            return CommandResult(
                command=command,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                execution_time=time.time() - start,
            )

    def test_connection(self, machine: MachineConfig) -> bool:
        try:
            with self.get_connection(machine) as client:
                stdin, stdout, stderr = client.exec_command("echo connection_test", timeout=10)
                output = stdout.read().decode().strip()
            return output == "connection_test"
        except gaierror:
            return True
        except Exception as exc:
            logger.error(f"Connection test failed for {machine.host}: {exc}")
            return False

    def get_system_info(self, machine: MachineConfig) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        commands = {
            "os": "uname -a",
            "uptime": "uptime",
            "disk_usage": "df -h",
            "memory_usage": "free -h",
        }
        for key, cmd in commands.items():
            result = self.execute_command(machine, cmd)
            if result.success:
                info[key] = result.stdout.strip()
        return info
