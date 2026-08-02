"""
Tests pour l'interpréteur Bou.Bel
"""

import sys
import os
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.lexer.tokenizer import Tokenizer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter


class TestInterpreter:
    def test_variables(self):
        code = "khdem x = 42; ikteb(x);"
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        # Capturer la sortie
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout
        
        assert "42" in output

    def test_addition(self):
        code = "khdem result = 5 + 3; ikteb(result);"
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout
        
        assert "8" in output

    def test_if_statement(self):
        code = """
        khdem score = 85;
        ken score >= 75 a3mel {
            ikteb("Bien!");
        } sinon {
            ikteb("Échec!");
        }
        """
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout
        
        assert "Bien!" in output

    def test_function(self):
        code = """
        dallel addition(a, b) {
            rejje a + b;
        }
        khdem result = addition(5, 3);
        ikteb(result);
        """
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout
        
        assert "8" in output

    def test_for_loop(self):
        code = """
        i men 1 7ata 3 a3mel {
            ikteb(i);
        }
        """
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout
        
        assert "1\n2\n3" in output


def run_tests():
    test = TestInterpreter()
    methods = [m for m in dir(test) if m.startswith('test_')]
    passed = 0
    failed = 0
    
    print("🧪 Running Interpreter tests...")
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
            import traceback
            traceback.print_exc()
            print(f"❌ {method}: {e}")
            failed += 1
    
    print("-" * 40)
    print(f"📊 Résultats: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    run_tests()