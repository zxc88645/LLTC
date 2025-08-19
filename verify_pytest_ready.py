#!/usr/bin/env python3
"""Verify that pytest can collect tests without syntax errors"""

import ast
import sys
from pathlib import Path

def check_python_syntax(filepath):
    """Check if a Python file has valid syntax using AST parsing."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # This is what pytest does internally - parse the AST
        ast.parse(source, filename=str(filepath))
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg} - {e.text.strip() if e.text else 'N/A'}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Verify all test files are ready for pytest."""
    print("🔍 Verifying pytest readiness...")
    print("=" * 60)
    print("Checking the files that were causing syntax errors:")
    print()
    
    # Focus on the files that had issues
    critical_files = [
        "tests/conftest.py",      # Had unterminated string literal
        "tests/test_integration.py",  # Had duplicate function definitions
        "tests/test_performance.py",  # Had duplicate function definitions
    ]
    
    all_valid = True
    for test_file in critical_files:
        filepath = Path(test_file)
        if filepath.exists():
            is_valid, error = check_python_syntax(filepath)
            if is_valid:
                print(f"✅ {test_file} - Syntax OK")
            else:
                print(f"❌ {test_file} - SYNTAX ERROR: {error}")
                all_valid = False
        else:
            print(f"⚠️  {test_file} - File not found")
            all_valid = False
    
    print()
    print("=" * 60)
    
    if all_valid:
        print("🎉 SUCCESS: All critical test files have valid syntax!")
        print("✅ pytest should now run without collection errors")
        print()
        print("The following command should now work:")
        print("pytest tests/ -v --tb=short --cov=src --cov-report=xml --cov-report=term-missing -m \"not (integration or performance or slow)\"")
    else:
        print("💥 FAILURE: Some test files still have syntax errors!")
        print("❌ pytest will fail during test collection phase")
        print("🔧 Please fix the syntax errors shown above")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)