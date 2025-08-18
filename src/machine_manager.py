"""Machine configuration management."""

import json
import os
from typing import List, Optional, Dict
from pathlib import Path
from cryptography.fernet import Fernet
from datetime import datetime

from .models import MachineConfig


class MachineManager:
    """Manages SSH machine configurations with encrypted credential storage."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.machines_file = self.config_dir / "machines.json"
        self.key_file = self.config_dir / "key.key"
        
        # Initialize encryption
        self._init_encryption()
        
        # Load existing machines
        self.machines: Dict[str, MachineConfig] = self._load_machines()
    
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
    
    def _load_machines(self) -> Dict[str, MachineConfig]:
        """Load machine configurations from file."""
        if not self.machines_file.exists():
            return {}
        
        try:
            with open(self.machines_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            machines = {}
            for machine_id, machine_data in data.items():
                # Decrypt password if present
                if machine_data.get('password'):
                    machine_data['password'] = self._decrypt_password(machine_data['password'])
                
                machines[machine_id] = MachineConfig(**machine_data)
            
            return machines
        except Exception as e:
            print(f"Error loading machines: {e}")
            return {}
    
    def _save_machines(self):
        """Save machine configurations to file."""
        try:
            data = {}
            for machine_id, machine in self.machines.items():
                machine_dict = machine.dict()
                # Encrypt password before saving
                if machine_dict.get('password'):
                    machine_dict['password'] = self._encrypt_password(machine_dict['password'])
                data[machine_id] = machine_dict
            
            with open(self.machines_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Set restrictive permissions on config file
            os.chmod(self.machines_file, 0o600)
        except Exception as e:
            print(f"Error saving machines: {e}")
    
    def add_machine(self, machine: MachineConfig) -> bool:
        """Add a new machine configuration."""
        try:
            machine.updated_at = datetime.now()
            self.machines[machine.id] = machine
            self._save_machines()
            return True
        except Exception as e:
            print(f"Error adding machine: {e}")
            return False
    
    def update_machine(self, machine_id: str, updates: Dict) -> bool:
        """Update an existing machine configuration."""
        if machine_id not in self.machines:
            return False
        
        try:
            machine = self.machines[machine_id]
            for key, value in updates.items():
                if hasattr(machine, key):
                    setattr(machine, key, value)
            
            machine.updated_at = datetime.now()
            self._save_machines()
            return True
        except Exception as e:
            print(f"Error updating machine: {e}")
            return False
    
    def remove_machine(self, machine_id: str) -> bool:
        """Remove a machine configuration."""
        if machine_id not in self.machines:
            return False
        
        try:
            del self.machines[machine_id]
            self._save_machines()
            return True
        except Exception as e:
            print(f"Error removing machine: {e}")
            return False
    
    def get_machine(self, machine_id: str) -> Optional[MachineConfig]:
        """Get a specific machine configuration."""
        return self.machines.get(machine_id)
    
    def list_machines(self) -> List[MachineConfig]:
        """List all machine configurations."""
        return list(self.machines.values())
    
    def search_machines(self, query: str) -> List[MachineConfig]:
        """Search machines by name or description."""
        query = query.lower()
        results = []
        
        for machine in self.machines.values():
            if (query in machine.name.lower() or 
                (machine.description and query in machine.description.lower()) or
                query in machine.host.lower()):
                results.append(machine)
        
        return results