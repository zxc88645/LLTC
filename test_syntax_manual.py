#!/usr/bin/env python3
import ast

try:
    with open('tests/test_integration.py', 'r') as f:
        source = f.read()
    
    ast.parse(source, filename='tests/test_integration.py')
    print("✅ tests/test_integration.py has valid syntax")
except SyntaxError as e:
    print(f"❌ Syntax error in tests/test_integration.py:")
    print(f"  Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
    print(f"  Error: {e.msg}")
    if e.offset:
        print(f"  Position: {' ' * (e.offset - 1)}^")
except Exception as e:
    print(f"❌ Unexpected error: {e}")