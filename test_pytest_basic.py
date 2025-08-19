#!/usr/bin/env python3
"""Basic test to verify pytest can run without conftest.py errors."""

def test_basic_functionality():
    """A simple test to verify pytest works."""
    assert True

def test_string_operations():
    """Test basic string operations."""
    test_string = "Hello, World!"
    assert len(test_string) == 13
    assert test_string.lower() == "hello, world!"

def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15