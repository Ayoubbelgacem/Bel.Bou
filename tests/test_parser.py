# tests/test_parser.py
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser

def test_parser():
    code = """
    khdem x = 5;
    ikteb("Hello");
    ken x > 3 a3mel {
        ikteb("Big");
    }
    dallel add(a, b) {
        rejje a + b;
    }
    """
    
    print("=" * 50)
    print("Parser Test:")
    print("=" * 50)
    
    # Lexer
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"✅ Lexer: {len(tokens)} tokens generated")
    
    # Parser
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"✅ Parser: AST generated with {len(ast.statements)} statements")
    
    # Show AST structure
    print("\nAST Structure:")
    for i, stmt in enumerate(ast.statements):
        print(f"  {i+1}. {type(stmt).__name__}")

if __name__ == "__main__":
    test_parser()