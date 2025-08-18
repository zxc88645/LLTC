#!/usr/bin/env python3
"""Integration test script for Docker setup."""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, cwd=None, timeout=60):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_docker_build():
    """Test Docker image build."""
    print("Testing Docker build...")
    
    project_root = Path(__file__).parent
    success, stdout, stderr = run_command(
        "docker build -t ssh-ai-assistant-test .",
        cwd=project_root,
        timeout=300  # 5 minutes for build
    )
    
    if success:
        print("✓ Docker build successful")
        return True
    else:
        print(f"✗ Docker build failed: {stderr}")
        return False


def test_docker_run():
    """Test Docker container run."""
    print("Testing Docker container run...")
    
    # Test help command
    success, stdout, stderr = run_command(
        "docker run --rm ssh-ai-assistant-test --help",
        timeout=30
    )
    
    if success:
        print("✓ Docker container runs successfully")
        return True
    else:
        print(f"✗ Docker container run failed: {stderr}")
        return False


def test_docker_compose():
    """Test Docker Compose configuration."""
    print("Testing Docker Compose...")
    
    project_root = Path(__file__).parent
    
    # Test config validation
    success, stdout, stderr = run_command(
        "docker-compose config",
        cwd=project_root
    )
    
    if success:
        print("✓ Docker Compose configuration is valid")
        return True
    else:
        print(f"✗ Docker Compose configuration invalid: {stderr}")
        return False


def test_health_check():
    """Test health check script."""
    print("Testing health check script...")
    
    project_root = Path(__file__).parent
    success, stdout, stderr = run_command(
        "python healthcheck.py",
        cwd=project_root
    )
    
    if success:
        print("✓ Health check script works")
        return True
    else:
        print(f"✗ Health check script failed: {stderr}")
        return False


def cleanup():
    """Clean up test resources."""
    print("Cleaning up...")
    
    # Remove test image
    run_command("docker rmi ssh-ai-assistant-test", timeout=30)
    
    # Remove any dangling containers
    run_command("docker container prune -f", timeout=30)


def main():
    """Run all integration tests."""
    print("Starting Docker integration tests...\n")
    
    tests = [
        test_health_check,
        test_docker_build,
        test_docker_run,
        test_docker_compose,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    # Cleanup
    cleanup()
    
    # Summary
    print(f"Integration test results:")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All Docker integration tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())