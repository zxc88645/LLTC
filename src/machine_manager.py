"""Machine configuration management with database backend."""

from typing import List, Optional, Dict
from pathlib import Path

import os

from .models import MachineConfig
from .db_service import DatabaseService
from .database import init_database


class MachineManager:
    """Manages SSH machine configurations using SQLite database."""
    
    def __init__(self, config_dir: str = "config"):
        os.environ["DATABASE_DIR"] = config_dir
        init_database()
        self.db_service = DatabaseService(config_dir)

        # Migrate from JSON if exists
        self._migrate_from_json(config_dir)
    
    def _migrate_from_json(self, config_dir: str):
        """Migrate existing JSON configurations to database."""
        json_file = Path(config_dir) / "machines.json"
        if json_file.exists():
            print("Migrating machine configurations from JSON to database...")
            success = self.db_service.migrate_from_json(str(json_file))
            if success:
                print("Migration completed successfully.")
                # Optionally backup the JSON file
                backup_file = json_file.with_suffix('.json.backup')
                json_file.rename(backup_file)
                print(f"Original JSON file backed up to {backup_file}")
            else:
                print("Migration failed. Keeping original JSON file.")
    
    def add_machine(self, machine: MachineConfig) -> bool:
        """Add a new machine configuration."""
        return self.db_service.add_machine(machine)
    
    def update_machine(self, machine_id: str, updates: Dict) -> bool:
        """Update an existing machine configuration."""
        return self.db_service.update_machine(machine_id, updates)
    
    def remove_machine(self, machine_id: str) -> bool:
        """Remove a machine configuration."""
        return self.db_service.remove_machine(machine_id)
    
    def get_machine(self, machine_id: str) -> Optional[MachineConfig]:
        """Get a specific machine configuration."""
        return self.db_service.get_machine(machine_id)
    
    def list_machines(self) -> List[MachineConfig]:
        """List all machine configurations."""
        return self.db_service.list_machines()
    
    def search_machines(self, query: str) -> List[MachineConfig]:
        """Search machines by name or description."""
        return self.db_service.search_machines(query)