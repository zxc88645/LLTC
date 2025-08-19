#!/usr/bin/env python3
import ast

try:
    with open('tests/test_performance.py', 'r') as f:
        source = f.read()
    
    # Try to parse the file
    ast.parse(source, filename='tests/test_performance.py')
    print("✓ tests/test_performance.py has valid syntax")
except SyntaxError as e:
    print(f"✗ Syntax error in tests/test_performance.py:")
    print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
    print(f"  Error: {e.msg}")
except Exception as e:
    print(f"✗ Error: {e}")