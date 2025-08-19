"""Simple machine configuration manager using JSON storage."""

from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Dict, List, Optional

from .models import MachineConfig


class MachineManager:
    """Manage `MachineConfig` records with basic persistence.

    The manager stores machine configurations in a JSON file located inside the
    provided configuration directory.  Passwords are stored using base64
    encoding to mimic encryption and are decoded when machines are loaded.
    """

    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.config_dir / "machines.json"
        self.machines: Dict[str, MachineConfig] = {}
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self.store_path.exists():
            return
        data = json.loads(self.store_path.read_text())
        for machine_id, cfg in data.items():
            password = cfg.get("password")
            if password:
                try:
                    cfg["password"] = base64.b64decode(password.encode()).decode()
                except Exception:
                    cfg["password"] = None
            self.machines[machine_id] = MachineConfig(**cfg)

    def _save(self) -> None:
        data: Dict[str, Dict] = {}
        for machine_id, cfg in self.machines.items():
            entry = cfg.dict()
            if entry.get("password"):
                entry["password"] = base64.b64encode(entry["password"].encode()).decode()
            data[machine_id] = entry
        self.store_path.write_text(json.dumps(data, indent=2, default=str))

    # ------------------------------------------------------------------
    def add_machine(self, machine: MachineConfig) -> bool:
        if machine.id in self.machines:
            return False
        self.machines[machine.id] = machine
        self._save()
        return True

    def update_machine(self, machine_id: str, updates: Dict) -> bool:
        machine = self.machines.get(machine_id)
        if not machine:
            return False
        data = machine.dict()
        for key, value in updates.items():
            if value is not None:
                data[key] = value
        self.machines[machine_id] = MachineConfig(**data)
        self._save()
        return True

    def remove_machine(self, machine_id: str) -> bool:
        if machine_id not in self.machines:
            return False
        del self.machines[machine_id]
        self._save()
        return True

    def get_machine(self, machine_id: str) -> Optional[MachineConfig]:
        return self.machines.get(machine_id)

    def list_machines(self) -> List[MachineConfig]:
        return list(self.machines.values())

    def search_machines(self, query: str) -> List[MachineConfig]:
        q = query.lower()
        results: List[MachineConfig] = []
        for machine in self.machines.values():
            if (
                q in machine.name.lower()
                or (machine.description and q in machine.description.lower())
                or q in machine.host.lower()
            ):
                results.append(machine)
        return results
