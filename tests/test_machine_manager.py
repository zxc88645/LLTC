"""Tests for machine manager."""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.machine_manager import MachineManager
from src.models import MachineConfig


class TestMachineManager:
    """Test MachineManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MachineManager(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_machine(self):
        """Test adding a machine."""
        machine = MachineConfig(
            id="test-machine",
            name="Test Machine",
            host="192.168.1.100",
            username="testuser",
            password="testpass"
        )
        
        success = self.manager.add_machine(machine)
        assert success is True
        
        # Verify machine was added
        retrieved = self.manager.get_machine("test-machine")
        assert retrieved is not None
        assert retrieved.name == "Test Machine"
        assert retrieved.host == "192.168.1.100"
    
    def test_password_encryption(self):
        """Test password encryption/decryption."""
        machine = MachineConfig(
            id="secure-machine",
            name="Secure Machine",
            host="secure.example.com",
            username="secureuser",
            password="supersecret"
        )
        
        self.manager.add_machine(machine)
        
        # Create new manager instance to test persistence
        new_manager = MachineManager(config_dir=self.temp_dir)
        retrieved = new_manager.get_machine("secure-machine")
        
        assert retrieved is not None
        assert retrieved.password == "supersecret"  # Should be decrypted
    
    def test_list_machines(self):
        """Test listing machines."""
        machine1 = MachineConfig(
            id="machine1",
            name="Machine 1",
            host="host1.com",
            username="user1"
        )
        
        machine2 = MachineConfig(
            id="machine2",
            name="Machine 2",
            host="host2.com",
            username="user2"
        )
        
        self.manager.add_machine(machine1)
        self.manager.add_machine(machine2)
        
        machines = self.manager.list_machines()
        assert len(machines) == 2
        
        machine_ids = [m.id for m in machines]
        assert "machine1" in machine_ids
        assert "machine2" in machine_ids
    
    def test_update_machine(self):
        """Test updating a machine."""
        machine = MachineConfig(
            id="update-machine",
            name="Original Name",
            host="original.com",
            username="user"
        )
        
        self.manager.add_machine(machine)
        
        # Update machine
        success = self.manager.update_machine("update-machine", {
            "name": "Updated Name",
            "host": "updated.com"
        })
        
        assert success is True
        
        # Verify update
        updated = self.manager.get_machine("update-machine")
        assert updated.name == "Updated Name"
        assert updated.host == "updated.com"
        assert updated.username == "user"  # Should remain unchanged
    
    def test_remove_machine(self):
        """Test removing a machine."""
        machine = MachineConfig(
            id="remove-machine",
            name="Remove Me",
            host="remove.com",
            username="user"
        )
        
        self.manager.add_machine(machine)
        assert self.manager.get_machine("remove-machine") is not None
        
        # Remove machine
        success = self.manager.remove_machine("remove-machine")
        assert success is True
        
        # Verify removal
        assert self.manager.get_machine("remove-machine") is None
    
    def test_search_machines(self):
        """Test searching machines."""
        machine1 = MachineConfig(
            id="web-server",
            name="Web Server",
            host="web.example.com",
            username="webuser",
            description="Production web server"
        )
        
        machine2 = MachineConfig(
            id="db-server",
            name="Database Server",
            host="db.example.com",
            username="dbuser",
            description="Production database"
        )
        
        self.manager.add_machine(machine1)
        self.manager.add_machine(machine2)
        
        # Search by name
        results = self.manager.search_machines("web")
        assert len(results) == 1
        assert results[0].id == "web-server"
        
        # Search by description
        results = self.manager.search_machines("production")
        assert len(results) == 2
        
        # Search by host
        results = self.manager.search_machines("db.example")
        assert len(results) == 1
        assert results[0].id == "db-server"