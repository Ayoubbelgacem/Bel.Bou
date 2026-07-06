# tests/test_lexer_v2.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try importing differently
from src.lexer.lexer import Lexer
from src.lexer.token import TokenType

def test_lexer():
    code = 'khdem x = 5; ikteb("salam");'
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("=" * 50)
    print("Bou.Bel Lexer Test:")
    print("=" * 50)
    for token in tokens:
        print(token)
    print("=" * 50)
    print(f"Total: {len(tokens)} tokens")

if __name__ == "__main__":
    test_lexer()