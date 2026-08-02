"""
Tests pour le compilateur LLVM Bou.Bel
"""

import sys
import os
import tempfile
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.lexer.tokenizer import Tokenizer
from src.parser.parser import Parser
from src.compiler.llvm_compiler import LLVMCompiler


class TestCompiler:
    def test_compilation(self):
        code = "khdem x = 42; ikteb(x);"
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        compiler = LLVMCompiler(optimize=True, debug=False)
        result = compiler.compile(ast)
        
        assert result is not None
        assert "module" in result.lower() or "define" in result.lower()

    def test_executable_generation(self):
        code = "khdem x = 42; ikteb(x);"
        tokens = Tokenizer(code).tokenize()
        ast = Parser(tokens).parse()
        
        with tempfile.NamedTemporaryFile(suffix='.exe' if os.name == 'nt' else '.out', delete=False) as f:
            output_file = f.name
        
        try:
            compiler = LLVMCompiler(optimize=True, debug=False)
            result = compiler.compile(ast, output_file)
            
            assert result is not None
            # Vérifier que le fichier existe
            if isinstance(result, str):
                # Si le compilateur retourne un chemin
                assert os.path.exists(result) or os.path.exists(output_file)
        finally:
            # Nettoyer
            for f in [output_file, output_file + '.exe']:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass


def run_tests():
    test = TestCompiler()
    methods = [m for m in dir(test) if m.startswith('test_')]
    passed = 0
    failed = 0
    
    print("🧪 Running Compiler tests...")
    print("-" * 40)
    
    for method in methods:
        try:
            getattr(test, method)()
            print(f"✅ {method}")
            passed += 1
        except Exception as e:
            print(f"❌ {method}: {e}")
            failed += 1
    
    print("-" * 40)
    print(f"📊 Résultats: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    run_tests()