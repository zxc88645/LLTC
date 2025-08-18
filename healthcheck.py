#!/usr/bin/env python3
"""Health check script for Docker container."""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_health():
    """Perform basic health checks."""
    try:
        # Check if main modules can be imported
        from src.cli_interface import cli
        from src.ai_agent import AIAgent
        from src.machine_manager import MachineManager
        
        # Check if required directories exist
        required_dirs = ['/app/config', '/app/logs']
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                print(f"ERROR: Required directory {dir_path} does not exist")
                return False
        
        # Check if we can create a basic instance (without actual connections)
        try:
            machine_manager = MachineManager()
            print("SUCCESS: All health checks passed")
            return True
        except Exception as e:
            print(f"ERROR: Failed to initialize components: {e}")
            return False
            
    except ImportError as e:
        print(f"ERROR: Failed to import required modules: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during health check: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)