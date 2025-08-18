"""Tests for Docker configuration and deployment."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestDockerConfiguration(unittest.TestCase):
    """Test Docker configuration files and setup."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.dockerfile_path = self.project_root / "Dockerfile"
        self.docker_compose_path = self.project_root / "docker-compose.yml"
        self.dockerignore_path = self.project_root / ".dockerignore"

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists and is readable."""
        self.assertTrue(self.dockerfile_path.exists(), "Dockerfile should exist")
        self.assertTrue(self.dockerfile_path.is_file(), "Dockerfile should be a file")
        
        # Check if Dockerfile has basic required content
        with open(self.dockerfile_path, 'r') as f:
            content = f.read()
            self.assertIn("FROM python:", content)
            self.assertIn("COPY requirements.txt", content)
            self.assertIn("RUN pip install", content)
            self.assertIn("ENTRYPOINT", content)

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists and is readable."""
        self.assertTrue(self.docker_compose_path.exists(), "docker-compose.yml should exist")
        self.assertTrue(self.docker_compose_path.is_file(), "docker-compose.yml should be a file")
        
        # Check if docker-compose.yml has basic required content
        with open(self.docker_compose_path, 'r') as f:
            content = f.read()
            self.assertIn("version:", content)
            self.assertIn("services:", content)
            self.assertIn("ssh-ai-assistant:", content)
            self.assertIn("volumes:", content)

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists and contains appropriate exclusions."""
        self.assertTrue(self.dockerignore_path.exists(), ".dockerignore should exist")
        self.assertTrue(self.dockerignore_path.is_file(), ".dockerignore should be a file")
        
        # Check if .dockerignore has basic exclusions
        with open(self.dockerignore_path, 'r') as f:
            content = f.read()
            self.assertIn("__pycache__", content)
            self.assertIn("*.pyc", content)
            self.assertIn(".git", content)
            self.assertIn("tests/", content)

    def test_logs_directory_exists(self):
        """Test that logs directory exists for volume mounting."""
        logs_dir = self.project_root / "logs"
        self.assertTrue(logs_dir.exists(), "logs directory should exist")
        self.assertTrue(logs_dir.is_dir(), "logs should be a directory")

    def test_config_directory_exists(self):
        """Test that config directory exists for volume mounting."""
        config_dir = self.project_root / "config"
        self.assertTrue(config_dir.exists(), "config directory should exist")
        self.assertTrue(config_dir.is_dir(), "config should be a directory")

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists for Docker build."""
        requirements_path = self.project_root / "requirements.txt"
        self.assertTrue(requirements_path.exists(), "requirements.txt should exist")
        self.assertTrue(requirements_path.is_file(), "requirements.txt should be a file")
        
        # Check if requirements.txt has basic dependencies
        with open(requirements_path, 'r') as f:
            content = f.read()
            self.assertIn("paramiko", content)
            self.assertIn("click", content)
            self.assertIn("rich", content)

    def test_main_py_exists(self):
        """Test that main.py exists as the entry point."""
        main_py_path = self.project_root / "main.py"
        self.assertTrue(main_py_path.exists(), "main.py should exist")
        self.assertTrue(main_py_path.is_file(), "main.py should be a file")

    def test_docker_build_syntax(self):
        """Test that Dockerfile has valid syntax (if Docker is available)."""
        try:
            # Try to validate Dockerfile syntax
            result = subprocess.run(
                ["docker", "build", "--dry-run", "-f", str(self.dockerfile_path), "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            # If Docker is available, the command should not fail with syntax errors
            if result.returncode != 0 and "docker: command not found" not in result.stderr:
                self.fail(f"Dockerfile syntax validation failed: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Skip test if Docker is not available or times out
            self.skipTest("Docker not available for syntax validation")

    def test_docker_compose_syntax(self):
        """Test that docker-compose.yml has valid syntax (if docker-compose is available)."""
        try:
            # Try to validate docker-compose.yml syntax
            result = subprocess.run(
                ["docker-compose", "config"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            # If docker-compose is available, the command should not fail with syntax errors
            if result.returncode != 0 and "command not found" not in result.stderr:
                self.fail(f"docker-compose.yml syntax validation failed: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Skip test if docker-compose is not available or times out
            self.skipTest("docker-compose not available for syntax validation")


class TestDockerEnvironment(unittest.TestCase):
    """Test Docker environment configuration."""

    def test_python_version_compatibility(self):
        """Test that the specified Python version is compatible."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        # Check that we're using a supported Python version
        self.assertIn("python:3.11", content.lower())

    def test_security_user_setup(self):
        """Test that Dockerfile sets up a non-root user."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        # Check that we create and use a non-root user
        self.assertIn("useradd", content)
        self.assertIn("USER appuser", content)

    def test_volume_mount_paths(self):
        """Test that docker-compose.yml has correct volume mount paths."""
        docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        
        with open(docker_compose_path, 'r') as f:
            content = f.read()
            
        # Check for proper volume mounts
        self.assertIn("./config:/app/config", content)
        self.assertIn("./logs:/app/logs", content)


if __name__ == "__main__":
    unittest.main()