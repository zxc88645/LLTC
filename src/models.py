"""Data models for the SSH AI system."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MachineConfig(BaseModel):
    """Configuration for an SSH machine."""
    
    id: str = Field(..., description="Unique identifier for the machine")
    name: str = Field(..., description="Human-readable name for the machine")
    host: str = Field(..., description="SSH host IP or hostname")
    port: int = Field(default=22, description="SSH port")
    username: str = Field(..., description="SSH username")
    password: Optional[str] = Field(default=None, description="SSH password (encrypted)")
    private_key_path: Optional[str] = Field(default=None, description="Path to private key file")
    description: Optional[str] = Field(default=None, description="Machine description")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CommandResult(BaseModel):
    """Result of an SSH command execution."""
    
    command: str = Field(..., description="The executed command")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(..., description="Command exit code")
    execution_time: float = Field(..., description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.exit_code == 0


class UserIntent(BaseModel):
    """Parsed user intent from natural language input."""
    
    action: str = Field(..., description="The action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    confidence: float = Field(..., description="Confidence score (0-1)")
    original_text: str = Field(..., description="Original user input")


class ConversationContext(BaseModel):
    """Context for ongoing conversation."""
    
    session_id: str = Field(..., description="Unique session identifier")
    selected_machine: Optional[str] = Field(default=None, description="Currently selected machine ID")
    conversation_history: list = Field(default_factory=list, description="Conversation history")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)