"""AI Agent that orchestrates SSH operations based on natural language input."""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .models import MachineConfig, CommandResult, UserIntent, ConversationContext
from .machine_manager import MachineManager
from .ssh_manager import SSHManager
from .command_interpreter import CommandInterpreter
from .db_service import DatabaseService


logger = logging.getLogger(__name__)


class AIAgent:
    """Main AI agent that handles user interactions and SSH operations."""
    
    def __init__(self):
        self.machine_manager = MachineManager()
        self.ssh_manager = SSHManager()
        self.command_interpreter = CommandInterpreter()
        self.db_service = DatabaseService()
    
    def create_session(self) -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        self.db_service.create_session(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation context for a session."""
        return self.db_service.get_session(session_id)
    
    def select_machine(self, session_id: str, machine_id: str) -> Dict[str, Any]:
        """Select a machine for the current session."""
        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": "Invalid session"}
        
        machine = self.machine_manager.get_machine(machine_id)
        if not machine:
            return {"success": False, "error": "Machine not found"}
        
        # Test connection
        if not self.ssh_manager.test_connection(machine):
            return {"success": False, "error": "Cannot connect to machine"}
        
        # Update session with selected machine
        success = self.db_service.update_session_machine(session_id, machine_id)
        if not success:
            return {"success": False, "error": "Failed to update session"}
        
        # Add system message about machine selection
        self.db_service.add_message(
            session_id, 
            "system", 
            f"Selected machine: {machine.name} ({machine.host})"
        )
        
        return {
            "success": True,
            "machine": {
                "id": machine.id,
                "name": machine.name,
                "host": machine.host,
                "description": machine.description
            }
        }
    
    def process_command(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process a natural language command."""
        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": "Invalid session"}
        
        if not context.selected_machine:
            return {"success": False, "error": "No machine selected. Please select a machine first."}
        
        machine = self.machine_manager.get_machine(context.selected_machine)
        if not machine:
            return {"success": False, "error": "Selected machine not found"}
        
        # Add user message to conversation
        self.db_service.add_message(session_id, "user", user_input)
        
        # Interpret the command
        intent = self.command_interpreter.interpret_command(user_input)
        
        if intent.confidence < 0.5:
            suggestions = self.command_interpreter.get_command_suggestions(user_input)
            error_msg = "I don't understand that command."
            
            # Add assistant response
            self.db_service.add_message(session_id, "assistant", error_msg, {
                "suggestions": suggestions,
                "available_commands": self.command_interpreter.get_available_intents()
            })
            
            return {
                "success": False,
                "error": error_msg,
                "suggestions": suggestions,
                "available_commands": self.command_interpreter.get_available_intents()
            }
        
        # Execute the command(s)
        results = self._execute_intent(machine, intent, session_id)
        
        # Generate summary and add assistant response
        summary = self._generate_summary(intent, results)
        self.db_service.add_message(session_id, "assistant", summary, {
            "intent": intent.dict(),
            "results": [self._format_result(result) for result in results]
        })
        
        return {
            "success": True,
            "intent": intent.dict(),
            "results": [self._format_result(result) for result in results],
            "summary": summary
        }
    
    def _execute_intent(self, machine: MachineConfig, intent: UserIntent, session_id: str) -> List[CommandResult]:
        """Execute commands based on the interpreted intent."""
        commands = intent.parameters.get('commands', [])
        results = []
        
        for command in commands:
            try:
                result = self.ssh_manager.execute_command(machine, command)
                results.append(result)
                
                # Record command execution in database
                self.db_service.record_command_execution(
                    session_id=session_id,
                    machine_id=machine.id,
                    command=result.command,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.exit_code,
                    execution_time=result.execution_time
                )
                
                # For some commands, we might want to stop on failure
                if intent.action == 'install_cuda' and not result.success:
                    # For CUDA installation, if nvidia-smi fails, skip the rest
                    if command == 'nvidia-smi' and result.exit_code != 0:
                        skip_result = CommandResult(
                            command="CUDA installation skipped",
                            stdout="NVIDIA driver not found. Please install NVIDIA driver first.",
                            stderr="",
                            exit_code=0,
                            execution_time=0.0
                        )
                        results.append(skip_result)
                        
                        # Record the skip message
                        self.db_service.record_command_execution(
                            session_id=session_id,
                            machine_id=machine.id,
                            command=skip_result.command,
                            stdout=skip_result.stdout,
                            stderr=skip_result.stderr,
                            exit_code=skip_result.exit_code,
                            execution_time=skip_result.execution_time
                        )
                        break
                
            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}")
                error_result = CommandResult(
                    command=command,
                    stdout="",
                    stderr=str(e),
                    exit_code=-1,
                    execution_time=0.0
                )
                results.append(error_result)
                
                # Record the error
                self.db_service.record_command_execution(
                    session_id=session_id,
                    machine_id=machine.id,
                    command=error_result.command,
                    stdout=error_result.stdout,
                    stderr=error_result.stderr,
                    exit_code=error_result.exit_code,
                    execution_time=error_result.execution_time
                )
        
        return results
    
    def _format_result(self, result: CommandResult) -> Dict[str, Any]:
        """Format command result for display."""
        return {
            "command": result.command,
            "success": result.success,
            "output": result.stdout if result.success else result.stderr,
            "exit_code": result.exit_code,
            "execution_time": f"{result.execution_time:.2f}s"
        }
    
    def _generate_summary(self, intent: UserIntent, results: List[CommandResult]) -> str:
        """Generate a human-readable summary of the operation."""
        successful_commands = sum(1 for r in results if r.success)
        total_commands = len(results)
        
        if intent.action == 'check_os_version':
            if successful_commands > 0:
                # Extract OS info from results
                for result in results:
                    if result.success and result.stdout.strip():
                        return f"系統資訊: {result.stdout.strip()}"
                return "已成功檢查作業系統版本"
            else:
                return "無法檢查作業系統版本"
        
        elif intent.action == 'install_cuda':
            if successful_commands == total_commands:
                return "CUDA 安裝完成"
            elif successful_commands > 0:
                return f"CUDA 安裝部分完成 ({successful_commands}/{total_commands} 步驟成功)"
            else:
                return "CUDA 安裝失敗"
        
        elif intent.action == 'check_devices':
            if successful_commands > 0:
                return f"已檢查系統設備 ({successful_commands} 個檢查項目成功)"
            else:
                return "無法檢查系統設備"
        
        else:
            if successful_commands == total_commands:
                return f"操作完成 ({intent.parameters.get('description', intent.action)})"
            else:
                return f"操作部分完成 ({successful_commands}/{total_commands} 成功)"
    
    def list_machines(self) -> List[Dict[str, Any]]:
        """List all available machines."""
        machines = self.machine_manager.list_machines()
        return [
            {
                "id": machine.id,
                "name": machine.name,
                "host": machine.host,
                "port": machine.port,
                "description": machine.description,
                "created_at": machine.created_at.isoformat()
            }
            for machine in machines
        ]
    
    def add_machine(self, machine_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new machine configuration."""
        try:
            machine = MachineConfig(**machine_config)
            
            # Test connection before adding
            if not self.ssh_manager.test_connection(machine):
                return {"success": False, "error": "Cannot connect to machine with provided credentials"}
            
            success = self.machine_manager.add_machine(machine)
            if success:
                return {"success": True, "machine_id": machine.id}
            else:
                return {"success": False, "error": "Failed to save machine configuration"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_machine(self, machine_id: str) -> Dict[str, Any]:
        """Remove a machine configuration."""
        success = self.machine_manager.remove_machine(machine_id)
        return {"success": success}
    
    def get_conversation_history(self, session_id: str) -> Optional[List[Dict]]:
        """Get conversation history for a session."""
        context = self.get_session(session_id)
        if context:
            return context.conversation_history
        return None