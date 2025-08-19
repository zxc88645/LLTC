#!/usr/bin/env python3
"""Final comprehensive syntax check for all test files"""

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
    test_files = [
        "tests/conftest.py",
        "tests/test_integration.py", 
        "tests/test_ai_agent.py",
        "tests/test_command_interpreter.py",
        "tests/test_docker.py",
        "tests/test_machine_manager.py",
        "tests/test_models.py",
        "tests/test_performance.py",
        "tests/test_ssh_manager.py",
        "tests/test_web_app.py"
    ]
    
    print("🔍 Final syntax check of all test files...")
    print("=" * 50)
    
    all_valid = True
    for test_file in test_files:
        filepath = Path(test_file)
        if filepath.exists():
            is_valid, error = check_syntax(filepath)
            if is_valid:
                print(f"✅ {test_file}")
            else:
                print(f"❌ {test_file}: {error}")
                all_valid = False
        else:
            print(f"⚠️  {test_file}: File not found")
    
    print("=" * 50)
    if all_valid:
        print("🎉 SUCCESS: All test files have valid syntax!")
        print("✅ pytest should now run without syntax errors")
    else:
        print("💥 FAILURE: Some test files still have syntax errors!")
        print("❌ pytest will fail during test collection")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)