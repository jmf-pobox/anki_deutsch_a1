#!/usr/bin/env python3
"""Count lines of Python code in the src tree."""

import os
from pathlib import Path


def count_python_lines():
    """Count lines in all Python files in src directory."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("Error: src directory not found")
        return

    total_lines = 0
    file_count = 0

    for py_file in src_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                file_count += 1
        except (UnicodeDecodeError, IOError) as e:
            print(f"Warning: Could not read {py_file}: {e}")
            continue

    print(f"{total_lines} lines in {file_count} Python files")


if __name__ == "__main__":
    count_python_lines()