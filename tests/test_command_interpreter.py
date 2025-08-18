"""Tests for command interpreter."""

import pytest
from src.command_interpreter import CommandInterpreter


class TestCommandInterpreter:
    """Test CommandInterpreter class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.interpreter = CommandInterpreter()
    
    def test_check_os_version_chinese(self):
        """Test OS version check in Chinese."""
        intent = self.interpreter.interpret_command("幫我查看這台作業系統版本")
        
        assert intent.action == "check_os_version"
        assert intent.confidence > 0.5
        assert "commands" in intent.parameters
        assert any("uname" in cmd for cmd in intent.parameters["commands"])
    
    def test_check_os_version_english(self):
        """Test OS version check in English."""
        intent = self.interpreter.interpret_command("check os version")
        
        assert intent.action == "check_os_version"
        assert intent.confidence > 0.5
    
    def test_install_cuda_chinese(self):
        """Test CUDA installation in Chinese."""
        intent = self.interpreter.interpret_command("幫我安裝CUDA")
        
        assert intent.action == "install_cuda"
        assert intent.confidence > 0.5
        assert "commands" in intent.parameters
        assert any("cuda" in cmd.lower() for cmd in intent.parameters["commands"])
    
    def test_check_devices_chinese(self):
        """Test device check in Chinese."""
        intent = self.interpreter.interpret_command("幫我檢查當前裝置有哪些設備")
        
        assert intent.action == "check_devices"
        assert intent.confidence > 0.5
        assert "commands" in intent.parameters
        assert any("lspci" in cmd for cmd in intent.parameters["commands"])
    
    def test_unknown_command(self):
        """Test unknown command handling."""
        intent = self.interpreter.interpret_command("do something completely random")
        
        assert intent.action == "unknown"
        assert intent.confidence == 0.0
    
    def test_get_command_suggestions(self):
        """Test command suggestions."""
        suggestions = self.interpreter.get_command_suggestions("檢查")
        
        assert len(suggestions) > 0
        assert any("檢查" in suggestion for suggestion in suggestions)
    
    def test_get_available_intents(self):
        """Test getting available intents."""
        intents = self.interpreter.get_available_intents()
        
        assert "check_os_version" in intents
        assert "install_cuda" in intents
        assert "check_devices" in intents
    
    def test_add_custom_pattern(self):
        """Test adding custom command pattern."""
        self.interpreter.add_custom_pattern(
            intent="test_intent",
            patterns=["test pattern"],
            commands=["echo test"],
            description="Test command"
        )
        
        intent = self.interpreter.interpret_command("test pattern")
        assert intent.action == "test_intent"
        assert intent.confidence > 0.5