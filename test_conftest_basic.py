#!/usr/bin/env python3
"""Basic test to verify conftest.py works correctly."""

import pytest
import sys
import os

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

def test_conftest_fixtures():
    """Test that basic fixtures from conftest.py work."""
    # This is a minimal test to check if conftest.py loads without errors
    # The actual fixtures will be tested when pytest runs
    pass

if __name__ == "__main__":
    # Run this single test to verify conftest.py works
    pytest.main([__file__, "-v"])