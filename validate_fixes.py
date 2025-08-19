#!/usr/bin/env python3
"""Validation script to check if CI/CD fixes are working."""

import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if requirements.txt is valid."""
    print("Checking requirements.txt...")
    try:
        # Try to parse requirements.txt
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        # Check for duplicates
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                package_name = line.split(">=")[0].split("==")[0].split("~=")[0]
                if package_name in packages:
                    print(f"❌ Duplicate package found: {package_name}")
                    return False
                packages.append(package_name)
        
        print(f"✅ Requirements.txt is valid with {len(packages)} unique packages")
        return True
    except Exception as e:
        print(f"❌ Error checking requirements.txt: {e}")
        return False

def check_health_endpoint():
    """Check if health endpoint exists in web_app.py."""
    print("Checking health endpoint...")
    try:
        with open("src/web_app.py", "r") as f:
            content = f.read()
        
        if '@app.get("/health")' in content:
            print("✅ Health endpoint found in web_app.py")
            return True
        else:
            print("❌ Health endpoint not found in web_app.py")
            return False
    except Exception as e:
        print(f"❌ Error checking health endpoint: {e}")
        return False

def check_memory_profile_script():
    """Check if memory profiling script exists."""
    print("Checking memory profiling script...")
    try:
        if Path("memory_profile_test.py").exists():
            print("✅ Memory profiling script exists")
            return True
        else:
            print("❌ Memory profiling script not found")
            return False
    except Exception as e:
        print(f"❌ Error checking memory profiling script: {e}")
        return False

def check_pytest_config():
    """Check if pytest configuration is valid."""
    print("Checking pytest configuration...")
    try:
        with open("pytest.ini", "r") as f:
            content = f.read()
        
        # Check if timeout is configured
        if "timeout" in content:
            print("✅ Pytest timeout configuration found")
            return True
        else:
            print("❌ Pytest timeout configuration not found")
            return False
    except Exception as e:
        print(f"❌ Error checking pytest configuration: {e}")
        return False

def check_docker_config():
    """Check if Docker configuration is valid."""
    print("Checking Docker configuration...")
    try:
        # Check if docker-compose.yml exists
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False
        
        # Check if Dockerfile exists
        if not Path("Dockerfile").exists():
            print("❌ Dockerfile not found")
            return False
        
        print("✅ Docker configuration files exist")
        return True
    except Exception as e:
        print(f"❌ Error checking Docker configuration: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🔍 Validating CI/CD fixes...\n")
    
    checks = [
        ("Requirements.txt", check_requirements),
        ("Health endpoint", check_health_endpoint),
        ("Memory profiling script", check_memory_profile_script),
        ("Pytest configuration", check_pytest_config),
        ("Docker configuration", check_docker_config)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name} check failed")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All CI/CD fixes validated successfully!")
        return True
    else:
        print("❌ Some checks failed. Please review the fixes.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)