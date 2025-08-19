"""Core AI agent orchestrating machine management and command execution."""

from __future__ import annotations

import atexit
import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .machine_manager import MachineManager
from .ssh_manager import SSHManager
from .command_interpreter import CommandInterpreter
from .models import CommandResult, ConversationContext, MachineConfig, UserIntent


class AIAgent:
    """High level interface used by the tests and web application."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        if config_dir is None:
            config_dir = tempfile.mkdtemp()
            atexit.register(lambda d=config_dir: os.path.isdir(d) and __import__('shutil').rmtree(d, ignore_errors=True))
        self.machine_manager = MachineManager(config_dir=config_dir)
        self.ssh_manager = SSHManager()
        self.command_interpreter = CommandInterpreter()
        self.sessions: Dict[str, ConversationContext] = {}

    # ------------------------------------------------------------------
    # Session management
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationContext(session_id=session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        return self.sessions.get(session_id)

    def get_conversation_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        context = self.get_session(session_id)
        if not context:
            return None
        return context.conversation_history

    # ------------------------------------------------------------------
    # Machine management wrappers
    def add_machine(self, machine_config: Dict[str, Any]) -> Dict[str, Any]:
        machine = MachineConfig(**machine_config)
        if not self.ssh_manager.test_connection(machine):
            return {"success": False, "error": "Cannot connect to machine"}
        if not self.machine_manager.add_machine(machine):
            return {"success": False, "error": "Machine already exists"}
        return {"success": True, "machine_id": machine.id}

    def list_machines(self) -> List[Dict[str, Any]]:
        machines = self.machine_manager.list_machines()
        return [
            {
                "id": m.id,
                "name": m.name,
                "host": m.host,
                "description": m.description,
            }
            for m in machines
        ]

    def remove_machine(self, machine_id: str) -> Dict[str, Any]:
        if not self.machine_manager.remove_machine(machine_id):
            return {"success": False, "error": "Machine not found"}
        return {"success": True}

    # ------------------------------------------------------------------
    # Session-machine interaction
    def select_machine(self, session_id: str, machine_id: str) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": "Invalid session"}
        machine = self.machine_manager.get_machine(machine_id)
        if not machine:
            return {"success": False, "error": "Machine not found"}
        if not self.ssh_manager.test_connection(machine):
            return {"success": False, "error": "Cannot connect to machine"}
        context.selected_machine = machine_id
        context.last_activity = datetime.now()
        context.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "message_type": "system",
                "content": f"Selected machine: {machine.name} ({machine.host})",
            }
        )
        return {
            "success": True,
            "machine": {
                "id": machine.id,
                "name": machine.name,
                "host": machine.host,
                "description": machine.description,
            },
        }

    # ------------------------------------------------------------------
    def _execute_intent(self, machine: MachineConfig, intent: UserIntent, session_id: str) -> List[CommandResult]:
        results: List[CommandResult] = []
        for cmd in intent.parameters.get("commands", []):
            results.append(self.ssh_manager.execute_command(machine, cmd))
        return results

    def _format_result(self, result: CommandResult) -> Dict[str, Any]:
        return {
            "command": result.command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
        }

    def _generate_summary(self, intent: UserIntent, results: List[CommandResult]) -> str:
        if not results:
            return "No commands executed."
        return f"Executed {intent.action} with {len(results)} command(s)."

    def process_command(self, session_id: str, user_input: str) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": "Invalid session"}
        if not context.selected_machine:
            return {"success": False, "error": "No machine selected. Please select a machine first."}
        machine = self.machine_manager.get_machine(context.selected_machine)
        if not machine:
            return {"success": False, "error": "Selected machine not found"}

        context.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "message_type": "user",
                "content": user_input,
            }
        )

        intent = self.command_interpreter.interpret_command(user_input)
        if intent.confidence < 0.5:
            suggestions = self.command_interpreter.get_command_suggestions(user_input)
            error_msg = "I don't understand that command."
            context.conversation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "message_type": "assistant",
                    "content": error_msg,
                }
            )
            return {
                "success": False,
                "error": error_msg,
                "suggestions": suggestions,
                "available_commands": self.command_interpreter.get_available_intents(),
            }

        results = self._execute_intent(machine, intent, session_id)
        summary = self._generate_summary(intent, results)
        context.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "message_type": "assistant",
                "content": summary,
                "metadata": {
                    "intent": intent.dict(),
                    "results": [self._format_result(r) for r in results],
                },
            }
        )
        return {
            "success": True,
            "intent": intent.dict(),
            "results": [self._format_result(r) for r in results],
            "summary": summary,
        }
