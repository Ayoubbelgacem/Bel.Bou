# tests/test_interpreter.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter

def test_interpreter():
    code = """
    khdem x = 5;
    ikteb("Hello");
    ken x > 3 a3mel {
        ikteb("x is big");
    }
    dallel add(a, b) {
        rejje a + b;
    }
    khdem result = add(10, 20);
    ikteb("Result: " + result);
    """
    
    print("=" * 50)
    print("Interpreter Test:")
    print("=" * 50)
    
    # Lexer
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"✅ Lexer: {len(tokens)} tokens")
    
    # Parser
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"✅ Parser: {len(ast.statements)} statements")
    
    # Interpreter
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("✅ Interpreter: Execution complete!")

if __name__ == "__main__":
    test_interpreter()