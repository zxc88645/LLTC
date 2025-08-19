#!/usr/bin/env python3
"""Memory profiling script for SSH AI Assistant."""

import sys
from pathlib import Path
from memory_profiler import profile

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

@profile
def test_memory_usage():
    """Test memory usage of core components."""
    print("Testing memory usage of SSH AI Assistant components...")
    
    # Test imports
    from src.models import MachineConfig, CommandResult, UserIntent
    from src.machine_manager import MachineManager
    from src.ssh_manager import SSHManager
    from src.command_interpreter import CommandInterpreter
    from src.ai_agent import AIAgent
    
    print("✓ All modules imported")
    
    # Test AI agent creation and basic operations
    agent = AIAgent()
    print("✓ AI agent created")
    
    # Create multiple sessions to test memory usage
    sessions = []
    for i in range(10):
        session_id = agent.create_session()
        sessions.append(session_id)
    
    print(f"✓ Created {len(sessions)} sessions")
    
    # Test command interpretation
    interpreter = CommandInterpreter()
    test_commands = [
        "幫我查看這台作業系統版本",
        "幫我安裝CUDA",
        "幫我檢查當前裝置有哪些設備",
        "幫我重啟系統",
        "幫我查看系統資源使用情況"
    ]
    
    for command in test_commands:
        intent = interpreter.interpret_command(command)
        print(f"✓ Interpreted command: {command} -> {intent.action}")
    
    # Test machine manager
    manager = MachineManager()
    test_machine = {
        "id": "memory-test-machine",
        "name": "Memory Test Machine",
        "host": "192.168.1.100",
        "username": "testuser",
        "password": "testpass"
    }
    
    manager.add_machine(test_machine)
    machines = manager.list_machines()
    print(f"✓ Machine manager operations completed, {len(machines)} machines")
    
    print("Memory profiling test completed successfully!")

if __name__ == "__main__":
    test_memory_usage()