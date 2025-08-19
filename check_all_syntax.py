#!/usr/bin/env python3
"""Check syntax of all test files"""

import ast
import os
from pathlib import Path

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source, filename=str(filepath))
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg} - {e.text.strip() if e.text else 'N/A'}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check syntax of all Python files in tests directory."""
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
    
    print("🔍 Checking syntax of test files...")
    all_valid = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            is_valid, error = check_file_syntax(test_file)
            if is_valid:
                print(f"✅ {test_file}")
            else:
                print(f"❌ {test_file}: {error}")
                all_valid = False
        else:
            print(f"⚠️  {test_file}: File not found")
    
    if all_valid:
        print("\n🎉 All test files have valid syntax!")
    else:
        print("\n💥 Some test files have syntax errors!")
    
    return all_valid

if __name__ == "__main__":
    main()