#!/usr/bin/env python3
"""Comprehensive syntax checker for all test files"""

import ast
import sys
from pathlib import Path

def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source, filename=str(filepath))
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check syntax of all test files."""
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ Tests directory not found!")
        return False
    
    test_files = list(test_dir.glob("*.py"))
    if not test_files:
        print("❌ No Python test files found!")
        return False
    
    print(f"🔍 Checking syntax of {len(test_files)} test files...")
    
    all_valid = True
    for test_file in sorted(test_files):
        is_valid, error = check_syntax(test_file)
        if is_valid:
            print(f"✅ {test_file.name}")
        else:
            print(f"❌ {test_file.name}: {error}")
            all_valid = False
    
    if all_valid:
        print("\n🎉 All test files have valid syntax!")
        return True
    else:
        print("\n💥 Some test files have syntax errors!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)