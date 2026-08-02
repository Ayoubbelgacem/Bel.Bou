"""
Tests pour l'optimiseur AST
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.parser.ast import *
from src.optimizer.ast_optimizer import ASTOptimizer


class TestOptimizer:
    def test_constant_folding_addition(self):
        node = BinOpNode(NumberNode(5), Token('PLUS'), NumberNode(3))
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        assert isinstance(result, NumberNode)
        assert result.value == 8

    def test_constant_folding_multiplication(self):
        node = BinOpNode(NumberNode(4), Token('STAR'), NumberNode(2))
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        assert isinstance(result, NumberNode)
        assert result.value == 8

    def test_constant_folding_division(self):
        node = BinOpNode(NumberNode(10), Token('SLASH'), NumberNode(2))
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        assert isinstance(result, NumberNode)
        assert result.value == 5.0

    def test_constant_folding_comparison(self):
        node = BinOpNode(NumberNode(5), Token('GREATER'), NumberNode(3))
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        assert isinstance(result, BooleanNode)
        assert result.value == True

    def test_optimize_if_true(self):
        node = IfNode(BooleanNode(True), [PrintNode(StringNode("Vrai"))], [PrintNode(StringNode("Faux"))])
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        # Doit retourner une liste contenant seulement le then_body
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PrintNode)
        assert isinstance(result[0].value, StringNode)
        assert result[0].value.value == "Vrai"

    def test_optimize_if_false(self):
        node = IfNode(BooleanNode(False), [PrintNode(StringNode("Vrai"))], [PrintNode(StringNode("Faux"))])
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PrintNode)
        assert isinstance(result[0].value, StringNode)
        assert result[0].value.value == "Faux"

    def test_optimize_nested_binop(self):
        node = BinOpNode(
            BinOpNode(NumberNode(2), Token('PLUS'), NumberNode(3)),
            Token('STAR'),
            NumberNode(4)
        )
        optimizer = ASTOptimizer()
        result = optimizer.optimize(node)
        
        # (2+3)*4 = 20
        assert isinstance(result, NumberNode)
        assert result.value == 20


def run_tests():
    test = TestOptimizer()
    methods = [m for m in dir(test) if m.startswith('test_')]
    passed = 0
    failed = 0
    
    print("🧪 Running Optimizer tests...")
    print("-" * 40)
    
    for method in methods:
        try:
            getattr(test, method)()
            print(f"✅ {method}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {method}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {method}: {e}")
            failed += 1
    
    print("-" * 40)
    print(f"📊 Résultats: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    run_tests()