#!/usr/bin/env python3
"""Simple syntax checker for Python files"""

import ast
import sys

def check_syntax(filename):
    try:
        with open(filename, 'r') as f:
            source = f.read()
        
        # Try to parse the file
        ast.parse(source, filename=filename)
        print(f"✓ {filename} has valid syntax")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {filename}:")
        print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
        print(f"  {' ' * (e.offset - 1 if e.offset else 0)}^")
        print(f"  {e.msg}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filename}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tests/test_performance.py"
    
    success = check_syntax(filename)
    sys.exit(0 if success else 1)