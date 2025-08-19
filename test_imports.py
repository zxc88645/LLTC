#!/usr/bin/env python3
"""Test that all test modules can be imported without syntax errors"""

import sys
import importlib.util

def test_import_module(module_path, module_name):
    """Test importing a module from file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            return False, f"Could not create spec for {module_path}"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Import error: {e}"

def main():
    """Test importing all test modules."""
    test_modules = [
        ("tests/conftest.py", "conftest"),
        ("tests/test_integration.py", "test_integration"),
        ("tests/test_performance.py", "test_performance"),
    ]
    
    print("🔍 Testing module imports...")
    print("=" * 40)
    
    all_success = True
    for module_path, module_name in test_modules:
        success, error = test_import_module(module_path, module_name)
        if success:
            print(f"✅ {module_path}")
        else:
            print(f"❌ {module_path}: {error}")
            all_success = False
    
    print("=" * 40)
    if all_success:
        print("🎉 All modules imported successfully!")
        print("✅ No syntax errors detected")
    else:
        print("💥 Some modules failed to import!")
        print("❌ Syntax errors still present")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)