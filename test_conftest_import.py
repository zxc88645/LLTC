#!/usr/bin/env python3
"""Test if conftest.py can be imported without syntax errors."""

import sys
import os

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

try:
    # Try to compile the conftest.py file
    with open('/workspace/tests/conftest.py', 'r') as f:
        source = f.read()
    
    # Compile the source code
    compile(source, '/workspace/tests/conftest.py', 'exec')
    print("✓ conftest.py compiles successfully - no syntax errors!")
    
except SyntaxError as e:
    print(f"✗ Syntax error in conftest.py:")
    print(f"  File: {e.filename}")
    print(f"  Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
    print(f"  Error: {e.msg}")
    if e.offset:
        print(f"  Position: {' ' * (e.offset - 1)}^")
    sys.exit(1)
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)

print("All syntax checks passed!")