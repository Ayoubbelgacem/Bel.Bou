#!/usr/bin/env python3
"""
Script pour exécuter les tests avec pytest
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    try:
        import pytest
        has_pytest = True
    except ImportError:
        has_pytest = False
    
    if has_pytest:
        print("🧪 Running tests with pytest...")
        return subprocess.call([sys.executable, '-m', 'pytest', 'tools/tests', '-v'])
    else:
        print("⚠️ pytest not installed. Running legacy tests...")
        from tools.tests.run_all_tests import main as run_legacy
        return run_legacy()


if __name__ == "__main__":
    sys.exit(main())