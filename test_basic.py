#!/usr/bin/env python3
"""Basic functionality test for SSH AI Assistant."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.models import MachineConfig, CommandResult, UserIntent
        from src.machine_manager import MachineManager
        from src.ssh_manager import SSHManager
        from src.command_interpreter import CommandInterpreter
        from src.ai_agent import AIAgent
        from src.cli_interface import CLIInterface
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_command_interpretation():
    """Test command interpretation."""
    try:
        from src.command_interpreter import CommandInterpreter
        
        interpreter = CommandInterpreter()
        
        # Test Chinese commands
        test_cases = [
            ("幫我查看這台作業系統版本", "check_os_version"),
            ("幫我安裝CUDA", "install_cuda"),
            ("幫我檢查當前裝置有哪些設備", "check_devices"),
        ]
        
        for command, expected_action in test_cases:
            intent = interpreter.interpret_command(command)
            if intent.action == expected_action and intent.confidence > 0.5:
                print(f"✓ Command '{command}' -> {intent.action} (confidence: {intent.confidence:.2f})")
            else:
                print(f"✗ Command '{command}' -> {intent.action} (confidence: {intent.confidence:.2f})")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Command interpretation error: {e}")
        return False

def test_machine_config():
    """Test machine configuration."""
    try:
        from src.models import MachineConfig
        
        machine = MachineConfig(
            id="test-machine",
            name="Test Machine",
            host="192.168.1.100",
            username="testuser",
            password="testpass"
        )
        
        assert machine.id == "test-machine"
        assert machine.port == 22  # default value
        print("✓ Machine configuration model works")
        return True
    except Exception as e:
        print(f"✗ Machine config error: {e}")
        return False

def test_ai_agent():
    """Test AI agent basic functionality."""
    try:
        from src.ai_agent import AIAgent
        
        agent = AIAgent()
        
        # Test session creation
        session_id = agent.create_session()
        assert session_id is not None
        assert len(session_id) > 0
        
        context = agent.get_session(session_id)
        assert context is not None
        assert context.session_id == session_id
        
        print("✓ AI agent session management works")
        return True
    except Exception as e:
        print(f"✗ AI agent error: {e}")
        return False

def main():
    """Run basic tests."""
    print("Running basic functionality tests...\n")
    
    tests = [
        test_imports,
        test_command_interpretation,
        test_machine_config,
        test_ai_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! The system is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)