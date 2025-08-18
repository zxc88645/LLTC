#!/usr/bin/env python3
"""Main entry point for the SSH AI Assistant."""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli_interface import cli


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ssh_ai.log'),
            logging.StreamHandler()
        ]
    )


if __name__ == "__main__":
    setup_logging()
    cli()