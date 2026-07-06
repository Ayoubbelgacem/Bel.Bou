# src/cli/repl.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter

class REPL:
    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
        self.variables = {}
    
    def start(self):
        print("=" * 50)
        print("🐪 Bou.Bel v1.0 - REPL")
        print("=" * 50)
        print("Type 'exit' or 'quit' to exit")
        print("Type 'help' for help")
        print("=" * 50)
        
        while True:
            try:
                code = input("Bou.Bel> ")
                
                if code.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                if code.lower() == 'help':
                    self.show_help()
                    continue
                
                if code.lower() == 'vars':
                    self.show_variables()
                    continue
                
                if code.strip() == '':
                    continue
                
                self.history.append(code)
                
                # Parse and execute
                try:
                    lexer = Lexer(code)
                    tokens = lexer.tokenize()
                    
                    parser = Parser(tokens)
                    ast = parser.parse()
                    
                    if ast.statements:
                        self.interpreter.interpret(ast, is_repl=True)
                        self.variables = self.interpreter.environment
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    def show_help(self):
        print("""
        📖 Bou.Bel Help:
        
        Variables:  khdem x = 5;
        Print:      ikteb("Hello");
        If:         ken x > 3 a3mel { ... } sinon { ... }
        For:        i men 1 7ata 5 a3mel { ... }
        Function:   dallel add(a, b) { rejje a + b; }
        Class:      class Animal { hetha.name = "Unknown"; }
        Array:      khdem notes = [1, 2, 3];
        File:       ikteb_fi_mlf("file.txt", "content");
        
        Commands:
          help  - Show this help
          vars  - Show variables
          exit  - Exit REPL
        """)
    
    def show_variables(self):
        if not self.variables:
            print("No variables defined")
            return
        print("Variables:")
        for name, value in self.variables.items():
            print(f"  {name} = {value}")

if __name__ == "__main__":
    repl = REPL()
    repl.start()