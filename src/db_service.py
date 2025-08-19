"""Database service layer for machine and session management."""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from pathlib import Path
import os

from .database import get_db, SessionLocal
from .db_models import Machine, ConversationSession, ConversationMessage, CommandExecution
from .models import MachineConfig, ConversationContext


class DatabaseService:
    """Service layer for database operations with encryption support."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / "key.key"
        
        # Initialize encryption
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption key for password storage."""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.cipher = Fernet(f.read())
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self.cipher = Fernet(key)
            # Set restrictive permissions on key file
            os.chmod(self.key_file, 0o600)
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt a password for storage."""
        if not password:
            return ""
        return self.cipher.encrypt(password.encode()).decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt a stored password."""
        if not encrypted_password:
            return ""
        return self.cipher.decrypt(encrypted_password.encode()).decode()
    
    def _machine_to_config(self, machine: Machine) -> MachineConfig:
        """Convert database Machine to MachineConfig."""
        return MachineConfig(
            id=machine.id,
            name=machine.name,
            host=machine.host,
            port=machine.port,
            username=machine.username,
            password=self._decrypt_password(machine.password) if machine.password else None,
            private_key_path=machine.private_key_path,
            description=machine.description,
            created_at=machine.created_at,
            updated_at=machine.updated_at
        )
    
    def add_machine(self, machine_config: MachineConfig) -> bool:
        """Add a new machine configuration."""
        try:
            with SessionLocal() as db:
                machine = Machine(
                    id=machine_config.id,
                    name=machine_config.name,
                    host=machine_config.host,
                    port=machine_config.port,
                    username=machine_config.username,
                    password=self._encrypt_password(machine_config.password) if machine_config.password else None,
                    private_key_path=machine_config.private_key_path,
                    description=machine_config.description,
                    created_at=machine_config.created_at,
                    updated_at=datetime.now()
                )
                db.add(machine)
                db.commit()
                return True
        except Exception as e:
            print(f"Error adding machine: {e}")
            return False
    
    def update_machine(self, machine_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing machine configuration."""
        try:
            with SessionLocal() as db:
                machine = db.query(Machine).filter(Machine.id == machine_id).first()
                if not machine:
                    return False
                
                for key, value in updates.items():
                    if key == 'password' and value:
                        value = self._encrypt_password(value)
                    if hasattr(machine, key):
                        setattr(machine, key, value)
                
                machine.updated_at = datetime.now()
                db.commit()
                return True
        except Exception as e:
            print(f"Error updating machine: {e}")
            return False
    
    def remove_machine(self, machine_id: str) -> bool:
        """Remove a machine configuration."""
        try:
            with SessionLocal() as db:
                machine = db.query(Machine).filter(Machine.id == machine_id).first()
                if not machine:
                    return False
                
                db.delete(machine)
                db.commit()
                return True
        except Exception as e:
            print(f"Error removing machine: {e}")
            return False
    
    def get_machine(self, machine_id: str) -> Optional[MachineConfig]:
        """Get a specific machine configuration."""
        try:
            with SessionLocal() as db:
                machine = db.query(Machine).filter(Machine.id == machine_id).first()
                if machine:
                    return self._machine_to_config(machine)
                return None
        except Exception as e:
            print(f"Error getting machine: {e}")
            return None
    
    def list_machines(self) -> List[MachineConfig]:
        """List all machine configurations."""
        try:
            with SessionLocal() as db:
                machines = db.query(Machine).all()
                return [self._machine_to_config(machine) for machine in machines]
        except Exception as e:
            print(f"Error listing machines: {e}")
            return []
    
    def search_machines(self, query: str) -> List[MachineConfig]:
        """Search machines by name or description."""
        try:
            query = query.lower()
            with SessionLocal() as db:
                machines = db.query(Machine).filter(
                    Machine.name.ilike(f"%{query}%") |
                    Machine.description.ilike(f"%{query}%") |
                    Machine.host.ilike(f"%{query}%")
                ).all()
                return [self._machine_to_config(machine) for machine in machines]
        except Exception as e:
            print(f"Error searching machines: {e}")
            return []
    
    def create_session(self, session_id: str) -> bool:
        """Create a new conversation session."""
        try:
            with SessionLocal() as db:
                session = ConversationSession(
                    id=session_id,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    is_active=True
                )
                db.add(session)
                db.commit()
                return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation session."""
        try:
            with SessionLocal() as db:
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                
                if not session:
                    return None
                
                # Get conversation history
                messages = db.query(ConversationMessage).filter(
                    ConversationMessage.session_id == session_id
                ).order_by(ConversationMessage.timestamp).all()
                
                conversation_history = []
                for msg in messages:
                    history_item = {
                        "timestamp": msg.timestamp.isoformat(),
                        "message_type": msg.message_type,
                        "content": msg.content
                    }
# Import logging at the top of the file
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

                return [self._machine_to_config(machine) for machine in machines]
        except Exception as e:
            logger.error(f"Error searching machines: {e}")
            return []
    
    def create_session(self, session_id: str) -> bool:
        """Create a new conversation session."""
        try:
            with SessionLocal() as db:
                session = ConversationSession(
                    id=session_id,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    is_active=True
                )
                db.add(session)
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation session."""
        try:
            with SessionLocal() as db:
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                
                if not session:
                    return None
                
                # Get conversation history
                messages = db.query(ConversationMessage).filter(
                    ConversationMessage.session_id == session_id
                ).order_by(ConversationMessage.timestamp).all()
                
                conversation_history = []
                for msg in messages:
                    history_item = {
                        "timestamp": msg.timestamp.isoformat(),
                        "message_type": msg.message_type,
                        "content": msg.content
                    }
                    if msg.extra_data:
                        history_item["metadata"] = json.loads(msg.extra_data)
                    conversation_history.append(history_item)
                
                return ConversationContext(
                    session_id=session.id,
                    selected_machine=session.machine_id,
                    conversation_history=conversation_history,
                    created_at=session.created_at,
                    last_activity=session.last_activity
                )
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def update_session_machine(self, session_id: str, machine_id: str) -> bool:
        """Update the selected machine for a session."""
        try:
            with SessionLocal() as db:
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                
                if not session:
                    return False
                
                session.machine_id = machine_id
                session.last_activity = datetime.now()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating session machine: {e}")
            return False
                        history_item["metadata"] = json.loads(msg.extra_data)
                    conversation_history.append(history_item)
                
                return ConversationContext(
                    session_id=session.id,
                    selected_machine=session.machine_id,
                    conversation_history=conversation_history,
                    created_at=session.created_at,
                    last_activity=session.last_activity
                )
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def update_session_machine(self, session_id: str, machine_id: str) -> bool:
        """Update the selected machine for a session."""
        try:
            with SessionLocal() as db:
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                
                if not session:
                    return False
                
                session.machine_id = machine_id
                session.last_activity = datetime.now()
                db.commit()
                return True
        except Exception as e:
            print(f"Error updating session machine: {e}")
            return False
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Dict = None) -> bool:
        """Add a message to conversation history."""
        try:
            with SessionLocal() as db:
                message = ConversationMessage(
                    session_id=session_id,
                    message_type=message_type,
                    content=content,
with SessionLocal() as db:
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                
                if not session:
                    return False
                
                session.machine_id = machine_id
                session.last_activity = datetime.now()
                db.commit()
                return True
        except Exception as e:
            # import logging
            logging.error(f"Error updating session machine: {e}")
            return False
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Dict = None) -> bool:
        """Add a message to conversation history."""
        try:
            with SessionLocal() as db:
                message = ConversationMessage(
                    session_id=session_id,
                    message_type=message_type,
                    content=content,
                    extra_data=json.dumps(metadata) if metadata else None,
                    timestamp=datetime.now()
                )
                db.add(message)

                # Update session last activity
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                if session:
                    session.last_activity = datetime.now()

                db.commit()
                return True
        except Exception as e:
            # import logging
            logging.error(f"Error adding message: {e}")
            return False
    
    def record_command_execution(self, session_id: str, machine_id: str, 
                               command: str, stdout: str, stderr: str, 
                               exit_code: int, execution_time: float) -> bool:
        """Record command execution in database."""
        try:
            with SessionLocal() as db:
                execution = CommandExecution(
                    session_id=session_id,
                    machine_id=machine_id,
                    command=command,
                    stdout=stdout,
                    timestamp=datetime.now()
                )
                db.add(message)
def add_message(self, session_id: str, message_type: str, content: str, metadata: Dict = None) -> bool:
        """Add a message to conversation history."""
        try:
            with SessionLocal() as db:
                current_time = datetime.now()
                message = ConversationMessage(
                    session_id=session_id,
                    message_type=message_type,
                    content=content,
                    extra_data=json.dumps(metadata) if metadata else None,
                    timestamp=current_time
                )
                db.add(message)

                # Update session last activity
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                if session:
                    session.last_activity = current_time

                db.commit()
                return True
        except Exception as e:
            print(f"Error adding message: {e}")
                # Update session last activity
                session = db.query(ConversationSession).filter(
                    ConversationSession.id == session_id
                ).first()
                if session:
                    session.last_activity = datetime.now()

                db.commit()
                return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def record_command_execution(self, session_id: str, machine_id: str, 
                               command: str, stdout: str, stderr: str, 
                               exit_code: int, execution_time: float) -> bool:
        """Record command execution in database."""
        try:
            with SessionLocal() as db:
                execution = CommandExecution(
                    session_id=session_id,
                    machine_id=machine_id,
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    execution_time=int(execution_time * 1000),  # Convert to milliseconds
                    timestamp=datetime.now()
                )
                db.add(execution)
                db.commit()
                return True
        except Exception as e:
            print(f"Error recording command execution: {e}")
            return False
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """Migrate machine configurations from JSON file to database."""
        try:
            json_path = Path(json_file_path)
            if not json_path.exists():
                return True  # No file to migrate
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for machine_id, machine_data in data.items():
                # Check if machine already exists
                existing = self.get_machine(machine_id)
                if existing:
                    continue  # Skip existing machines
                
                # Create MachineConfig and add to database
                machine_config = MachineConfig(**machine_data)
                self.add_machine(machine_config)
            
            return True
        except Exception as e:
            print(f"Error migrating from JSON: {e}")
            return False