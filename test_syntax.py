import ast

# Test syntax of conftest.py
try:
    with open('tests/conftest.py', 'r') as f:
        source = f.read()
    
    ast.parse(source, filename='tests/conftest.py')
    print("✓ conftest.py has valid syntax")
except SyntaxError as e:
    print(f"✗ Syntax error in conftest.py:")
    print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
    print(f"  Error: {e.msg}")
except Exception as e:
    print(f"✗ Error: {e}")