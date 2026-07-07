#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.cli.repl import REPL
from src.utils.errors import BouBelError

def run_file(filename, debug=False):
    """Execute a Bou.Bel file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"📂 Running: {filename}")
        print("-" * 50)
        
        lexer = Lexer(code)
        tokens = lexer.tokenize(debug=debug)
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.debug = debug
        interpreter.interpret(ast)
        
        print("-" * 50)
        print("✅ Program executed successfully")
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
    except BouBelError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(
        description="🐪 Bou.Bel - Tunisian Arabic Programming Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test.bou     - Run a Bou.Bel file
  python main.py -i           - Start interactive REPL
  python main.py -v           - Show version
  python main.py --debug test.bou  - Run with token/AST debug output
        """
    )
    parser.add_argument('file', nargs='?', help='Bou.Bel file to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive REPL')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.version:
        print("🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language")
        print("Copyright © 2024 Bou.Bel Team")
        return
    
    if args.file:
        run_file(args.file, debug=args.debug)
    elif args.interactive:
        repl = REPL(debug=args.debug)
        repl.start()
    else:
        # Default: show help with examples
        print("""
        🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language
        
        Usage:
          python main.py <file.bou>     - Run a Bou.Bel file
          python main.py -i            - Start interactive REPL
          python main.py -v            - Show version
          python main.py --debug -i    - Start REPL with debug mode
        
        Example Bou.Bel code:
          khdem x = 10;
          khdem y = 20;
          khdem z = x + y;
          ikteb(z);  // Affiche 30
          
          ken z > 25 a3mel {
              ikteb("z est grand");
          } sinon {
              ikteb("z est petit");
          }
        
        For more information, visit: https://github.com/boubel-lang
        """)

if __name__ == "__main__":
    main()