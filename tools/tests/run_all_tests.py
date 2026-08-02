#!/usr/bin/env python3
"""
Script pour exécuter tous les tests
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.tests import test_lexer, test_parser, test_interpreter, test_compiler, test_optimizer


def main():
    print("\n" + "=" * 60)
    print("🧪 EXÉCUTION DE TOUS LES TESTS")
    print("=" * 60 + "\n")
    
    total_passed = 0
    total_failed = 0
    
    # Lexer
    p, f = test_lexer.run_tests()
    total_passed += p
    total_failed += f
    print()
    
    # Interpreter
    p, f = test_interpreter.run_tests()
    total_passed += p
    total_failed += f
    print()
    
    # Compiler
    p, f = test_compiler.run_tests()
    total_passed += p
    total_failed += f
    print()
    
    # Optimizer
    p, f = test_optimizer.run_tests()
    total_passed += p
    total_failed += f
    print()
    
    print("=" * 60)
    print(f"📊 RÉSULTAT GLOBAL: {total_passed} passed, {total_failed} failed")
    print("=" * 60)
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())