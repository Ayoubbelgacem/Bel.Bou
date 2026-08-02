"""
Tests pour le lexer Bou.Bel
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.lexer.tokenizer import Tokenizer
from src.lexer.tokens import TokenType


class TestLexer:
    def test_basic_tokens(self):
        code = "khdem x = 42;"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) >= 4
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "khdem"
        assert tokens[2].type == TokenType.EQUALS
        assert tokens[3].value == 42

    def test_string_literals(self):
        code = 'khdem nom = "Ayoub";'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        # Trouver le token string
        found = False
        for t in tokens:
            if t.type == TokenType.STRING:
                assert t.value == "Ayoub"
                found = True
        assert found

    def test_comments(self):
        code = "# Ceci est un commentaire\nkhdem x = 5;"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        # Les commentaires ne doivent pas apparaître dans les tokens
        for t in tokens:
            assert t.type != TokenType.COMMENT

    def test_bin_ops(self):
        code = "5 + 3 * 2"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        types = [t.type for t in tokens]
        assert TokenType.NUMBER in types
        assert TokenType.PLUS in types
        assert TokenType.STAR in types

    def test_booleans(self):
        code = "s7i7 ghalet"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == "s7i7"
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == "ghalet"


def run_tests():
    test = TestLexer()
    methods = [m for m in dir(test) if m.startswith('test_')]
    passed = 0
    failed = 0
    
    print("🧪 Running Lexer tests...")
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