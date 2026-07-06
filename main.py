# main.py
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.cli.repl import REPL

def run_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bou.Bel Programming Language")
    parser.add_argument('file', nargs='?', help='File to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start REPL')
    
    args = parser.parse_args()
    
    if args.file:
        run_file(args.file)
    elif args.interactive:
        repl = REPL()
        repl.start()
    else:
        # Default: show help
        print("""
        🐪 Bou.Bel v1.0
        
        Usage:
          python main.py <file.bou>     - Run a file
          python main.py -i            - Start REPL
          python main.py               - Show this help
        """)

if __name__ == "__main__":
    main()

    