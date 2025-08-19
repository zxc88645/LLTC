#!/usr/bin/env python3
"""Integration test for CI/CD pipeline components."""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def test_requirements_installation():
    """Test that requirements can be installed without conflicts."""
    print("Testing requirements installation...")
    try:
        # Create a temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to create virtual environment: {result.stderr}")
                return False
            
            # Get pip path
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:  # Unix-like
                pip_path = venv_path / "bin" / "pip"
            
            # Install requirements
            result = subprocess.run([
                str(pip_path), "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install requirements: {result.stderr}")
                return False
            
            print("✅ Requirements installed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error testing requirements installation: {e}")
        return False

def test_basic_imports():
    """Test that basic imports work."""
    print("Testing basic imports...")
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Test core imports
        from src.models import MachineConfig, CommandResult, UserIntent
        from src.machine_manager import MachineManager
        from src.command_interpreter import CommandInterpreter
        from src.ai_agent import AIAgent
        
        print("✅ All core modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_memory_profiling_script():
    """Test that memory profiling script can run."""
    print("Testing memory profiling script...")
    try:
        # Check if script exists
        if not Path("memory_profile_test.py").exists():
            print("❌ Memory profiling script not found")
            return False
        
        # Try to run the script (dry run)
        result = subprocess.run([
            sys.executable, "-c", 
            "import memory_profile_test; print('Memory profiling script is importable')"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Memory profiling script has issues: {result.stderr}")
            return False
        
        print("✅ Memory profiling script is ready")
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory profiling script: {e}")
        return False

def test_health_endpoint():
    """Test that health endpoint works."""
    print("Testing health endpoint...")
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from fastapi.testclient import TestClient
        from src.web_app import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code != 200:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
        
        data = response.json()
        if "status" not in data:
            print("❌ Health endpoint response missing status")
            return False
        
        print(f"✅ Health endpoint working, status: {data['status']}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_pytest_markers():
    """Test that pytest markers are properly configured."""
    print("Testing pytest markers...")
    try:
        # Check if pytest.ini exists
        if not Path("pytest.ini").exists():
            print("❌ pytest.ini not found")
            return False
        
        # Read pytest.ini and check for markers
        with open("pytest.ini", "r") as f:
            content = f.read()
        
        required_markers = ["unit", "integration", "performance", "security", "slow"]
        for marker in required_markers:
            if f"{marker}:" not in content:
                print(f"❌ Marker '{marker}' not found in pytest.ini")
                return False
        
        print("✅ All required pytest markers are configured")
        return True
        
    except Exception as e:
        print(f"❌ Error testing pytest markers: {e}")
        return False

def test_docker_files():
    """Test that Docker files are valid."""
    print("Testing Docker configuration...")
    try:
        required_files = ["Dockerfile", "docker-compose.yml", "docker-compose.override.yml"]
        
        for file_name in required_files:
            if not Path(file_name).exists():
                print(f"❌ {file_name} not found")
                return False
        
        # Basic validation of docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        
        if "ssh-ai-assistant:" not in content:
            print("❌ docker-compose.yml missing main service")
            return False
        
        if "8000:8000" not in content:
            print("❌ docker-compose.yml missing port mapping")
            return False
        
        print("✅ Docker configuration files are valid")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Docker files: {e}")
        return False

def main():
    """Run all CI/CD integration tests."""
    print("🔧 Running CI/CD Integration Tests\n")
    
    tests = [
        ("Basic imports", test_basic_imports),
        ("Memory profiling script", test_memory_profiling_script),
        ("Health endpoint", test_health_endpoint),
        ("Pytest markers", test_pytest_markers),
        ("Docker files", test_docker_files),
        # Note: Requirements installation test is commented out as it's slow
        # ("Requirements installation", test_requirements_installation),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} test failed")
    
    print(f"\n📊 CI/CD Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CI/CD integration tests passed!")
        print("The CI/CD pipeline should now work correctly.")
        return True
    else:
        print("❌ Some CI/CD integration tests failed.")
        print("Please review the failing components before running the CI/CD pipeline.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)