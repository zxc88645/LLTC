#!/usr/bin/env python3
"""Main entry point for the SSH AI Assistant."""

import logging
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'ssh_ai.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check if running in CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        logger.info("Starting CLI interface...")
        from src.cli_interface import cli
        cli()
    else:
        # Default to web interface
        logger.info("Starting web interface...")
        
        # Initialize database
        from src.database import init_database
        init_database()
        
        # Start web server
        import uvicorn
        from src.web_app import app
        
        # Get configuration from environment variables
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', '8000'))
        
        logger.info(f"Starting web server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()